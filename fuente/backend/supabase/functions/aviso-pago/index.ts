// =====================================================================
//  POST /aviso-pago
//  Es la "comunicación on-line" de Cecabank: la llamada servidor a
//  servidor que avisa de que un pago se ha autorizado. Es la ÚNICA
//  fuente fiable de que un pedido está cobrado (la URL_OK depende de
//  que el cliente pulse ACEPTAR, así que no vale).
//
//  Hay que contestar en menos de 30 segundos con:
//    $*$OKY$*$   todo bien, pedido actualizado
//    $*$NOK$*$   no podemos servirlo -> Cecabank anula el cobro
// =====================================================================
import { createClient } from "jsr:@supabase/supabase-js@2";
import { avisoEsAutentico, type Comercio } from "../_compartido/ceca.ts";

const OKY = "$*$OKY$*$";
const NOK = "$*$NOK$*$";
const responder = (t: string) =>
  new Response(t, { status: 200, headers: { "content-type": "text/html; charset=utf-8" } });

Deno.serve(async (req) => {
  if (req.method !== "POST") return responder(NOK);

  const comercio: Comercio = {
    clave:       Deno.env.get("CECA_CLAVE") ?? "",
    merchantId:  Deno.env.get("CECA_MERCHANT_ID") ?? "",
    acquirerBin: Deno.env.get("CECA_ACQUIRER_BIN") ?? "",
    terminalId:  Deno.env.get("CECA_TERMINAL_ID") ?? "",
  };
  if (!comercio.clave) { console.error("falta CECA_CLAVE"); return responder(NOK); }

  // Cecabank envía los campos como un formulario
  const datos: Record<string, string> = {};
  try {
    const tipo = req.headers.get("content-type") ?? "";
    if (tipo.includes("application/json")) {
      Object.assign(datos, await req.json());
    } else {
      const form = await req.formData();
      for (const [k, v] of form.entries()) datos[k] = String(v);
    }
  } catch (e) {
    console.error("aviso ilegible", e);
    return responder(NOK);
  }

  const ref = (datos.Num_operacion ?? "").trim();
  if (!ref) { console.error("aviso sin Num_operacion"); return responder(NOK); }

  if (!(await avisoEsAutentico(comercio, datos))) {
    console.error("firma del aviso incorrecta", { ref });
    return responder(NOK);
  }

  const importeCent = Number((datos.Importe ?? "").replace(/^0+/, "") || "0");
  if (!Number.isInteger(importeCent) || importeCent <= 0) {
    console.error("importe raro en el aviso", { ref, importe: datos.Importe });
    return responder(NOK);
  }

  const db = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    { auth: { persistSession: false } },
  );

  const { data: resultado, error } = await db.rpc("confirmar_pedido", {
    p_ref: ref, p_importe_cent: importeCent,
  });

  if (error) {
    console.error("fallo al confirmar", { ref, error });
    return responder(NOK);          // mejor anular el cobro que cobrarlo a ciegas
  }

  if (resultado !== "ok") {
    console.error("pedido no confirmado", { ref, resultado });
    return responder(NOK);
  }

  // datos del cobro, para reclamaciones y devoluciones desde la consola
  await db.from("tienda_pedido").update({
    ceca_referencia:     datos.Referencia ?? null,
    ceca_num_aut:        datos.Num_aut ?? null,
    ceca_tipo_operacion: datos.Tipo_operacion ?? null,
    ceca_final_pan:      datos.FinalPAN ?? null,
  }).eq("ref", ref);

  avisarPorEmail(db, ref).catch((e) => console.error("aviso por email", e));

  return responder(OKY);
});

// ---------------------------------------------------------------------
//  Aviso por email (opcional): solo se envía si existe el secreto
//  RESEND_API_KEY. Si no, el pedido queda igualmente guardado.
// ---------------------------------------------------------------------
async function avisarPorEmail(db: ReturnType<typeof createClient>, ref: string) {
  const clave = Deno.env.get("RESEND_API_KEY");
  const destino = Deno.env.get("EMAIL_AVISOS");
  const remite = Deno.env.get("EMAIL_REMITE");
  if (!clave || !destino || !remite) return;

  const { data: pedido } = await db.from("tienda_pedido").select("*").eq("ref", ref).single();
  if (!pedido) return;
  const { data: lineas } = await db.from("tienda_linea").select("*").eq("pedido_id", pedido.id);

  const euros = (c: number) => (c / 100).toFixed(2).replace(".", ",") + " €";
  const detalle = (lineas ?? [])
    .map((l) => `- ${l.unidades} x ${l.nombre}${l.talla !== "U" ? " (talla " + l.talla + ")" : ""} — ${euros(l.precio_cent * l.unidades)}`)
    .join("\n");

  const texto = [
    `Pedido ${pedido.ref} — PAGADO`,
    "",
    detalle,
    pedido.envio_cent ? `- Envío — ${euros(pedido.envio_cent)}` : "- Recogida en el centro",
    `TOTAL: ${euros(pedido.total_cent)}`,
    "",
    `${pedido.nombre} · ${pedido.email} · ${pedido.telefono}`,
    pedido.entrega === "envio"
      ? `Envío a: ${pedido.direccion}, ${pedido.cp} ${pedido.poblacion} (${pedido.provincia})`
      : "Recoge en el centro",
    pedido.notas ? `Notas: ${pedido.notas}` : "",
    "",
    `Referencia de Cecabank: ${pedido.ceca_referencia ?? "-"}`,
  ].join("\n");

  await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { authorization: `Bearer ${clave}`, "content-type": "application/json" },
    body: JSON.stringify({
      from: remite, to: destino.split(","), reply_to: pedido.email,
      subject: `Pedido ${pedido.ref} — ${euros(pedido.total_cent)}`,
      text: texto,
    }),
  });
}
