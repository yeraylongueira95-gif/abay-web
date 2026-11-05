// =====================================================================
//  POST /crear-pedido
//  Recibe el carrito del navegador, vuelve a calcular el precio con los
//  datos de la base (NUNCA se fía del importe que manda el cliente),
//  guarda el pedido y devuelve el formulario firmado para el TPV.
// =====================================================================
import { createClient } from "jsr:@supabase/supabase-js@2";
import { formularioCompra, nuevaReferencia, type Comercio, type Entorno } from "../_compartido/ceca.ts";

const ORIGENES = [
  "https://abayperformance.com",
  "https://www.abayperformance.com",
  "http://localhost:8777",
];

const MAX_UNIDADES_PEDIDO = 10;
const MAX_POR_LINEA = 5;

function cors(origen: string | null) {
  const permitido = origen && ORIGENES.includes(origen) ? origen : ORIGENES[0];
  return {
    "Access-Control-Allow-Origin": permitido,
    "Access-Control-Allow-Headers": "content-type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Vary": "Origin",
  };
}

const json = (cuerpo: unknown, estado: number, cab: HeadersInit) =>
  new Response(JSON.stringify(cuerpo), {
    status: estado,
    headers: { ...cab, "content-type": "application/json; charset=utf-8" },
  });

Deno.serve(async (req) => {
  const cab = cors(req.headers.get("origin"));
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cab });

  // GET: lo que la web necesita saber para pintar la tienda (precios, stock, envío)
  if (req.method === "GET") return await catalogo(cab);

  if (req.method !== "POST") return json({ error: "método no permitido" }, 405, cab);

  const comercio: Comercio = {
    clave:       Deno.env.get("CECA_CLAVE") ?? "",
    merchantId:  Deno.env.get("CECA_MERCHANT_ID") ?? "",
    acquirerBin: Deno.env.get("CECA_ACQUIRER_BIN") ?? "",
    terminalId:  Deno.env.get("CECA_TERMINAL_ID") ?? "",
  };
  const entorno = (Deno.env.get("CECA_ENTORNO") ?? "pruebas") as Entorno;
  const web = Deno.env.get("WEB_URL") ?? "https://abayperformance.com";

  if (!comercio.clave || !comercio.merchantId || !comercio.acquirerBin || !comercio.terminalId) {
    console.error("faltan los secretos del TPV");
    return json({ error: "La tienda no está configurada todavía." }, 503, cab);
  }

  let cuerpo: Record<string, unknown>;
  try { cuerpo = await req.json(); }
  catch { return json({ error: "petición mal formada" }, 400, cab); }

  const db = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    { auth: { persistSession: false } },
  );

  // ---------- ajustes ----------
  const { data: ajustes } = await db.from("tienda_ajuste").select("clave, valor");
  const ajuste = (k: string) => ajustes?.find((a) => a.clave === k)?.valor ?? null;
  if (ajuste("pedidos_abiertos") !== "si") {
    return json({ error: "La tienda está cerrada ahora mismo. Escríbenos por WhatsApp." }, 503, cab);
  }
  const envioCentConf = ajuste("envio_cent");
  const envioDisponible = envioCentConf !== null && envioCentConf !== "" && Number(envioCentConf) >= 0;

  // ---------- carrito ----------
  const lineasPedidas = Array.isArray(cuerpo.lineas) ? cuerpo.lineas as Array<Record<string, unknown>> : [];
  if (lineasPedidas.length === 0 || lineasPedidas.length > 10) {
    return json({ error: "El carrito está vacío." }, 400, cab);
  }

  const { data: productos } = await db.from("tienda_producto").select("*").eq("activo", true);
  const { data: stock } = await db.from("tienda_stock").select("*");
  if (!productos || !stock) return json({ error: "No se pudo leer el catálogo." }, 500, cab);

  const lineas: Array<{ producto_id: string; nombre: string; talla: string; unidades: number; precio_cent: number }> = [];
  let subtotal = 0;

  for (const l of lineasPedidas) {
    const id = String(l.producto ?? "");
    const talla = String(l.talla ?? "U").toUpperCase();
    const unidades = Number(l.unidades ?? 0);

    const prod = productos.find((p) => p.id === id);
    if (!prod) return json({ error: "Hay un producto que ya no está a la venta." }, 400, cab);
    if (!Number.isInteger(unidades) || unidades < 1 || unidades > MAX_POR_LINEA) {
      return json({ error: "Cantidad no válida." }, 400, cab);
    }
    const fila = stock.find((s) => s.producto_id === id && s.talla === talla);
    if (!fila) return json({ error: `No tenemos la talla ${talla} de ${prod.nombre}.` }, 400, cab);
    if (fila.unidades < unidades) {
      return json({
        error: fila.unidades === 0
          ? `Se ha agotado la talla ${talla} de ${prod.nombre.toLowerCase()}.`
          : `Solo quedan ${fila.unidades} de ${prod.nombre.toLowerCase()} en talla ${talla}.`,
      }, 409, cab);
    }
    if (lineas.some((x) => x.producto_id === id && x.talla === talla)) {
      return json({ error: "El carrito tiene líneas repetidas." }, 400, cab);
    }

    lineas.push({ producto_id: id, nombre: prod.nombre, talla, unidades, precio_cent: prod.precio_cent });
    subtotal += prod.precio_cent * unidades;
  }

  const totalUnidades = lineas.reduce((n, l) => n + l.unidades, 0);
  if (totalUnidades > MAX_UNIDADES_PEDIDO) {
    return json({ error: `Por pedido admitimos ${MAX_UNIDADES_PEDIDO} unidades como máximo.` }, 400, cab);
  }

  // ---------- cliente ----------
  const c = (cuerpo.cliente ?? {}) as Record<string, unknown>;
  const txt = (v: unknown, max = 120) => String(v ?? "").trim().slice(0, max);
  const nombre = txt(c.nombre, 80);
  const email = txt(c.email, 120).toLowerCase();
  const telefono = txt(c.telefono, 30);
  const entrega = cuerpo.entrega === "envio" ? "envio" : "recogida";
  const metodo = cuerpo.metodo === "bizum" ? "bizum" : "tarjeta";

  if (nombre.length < 2) return json({ error: "Falta tu nombre." }, 400, cab);
  if (!/^[^@\s]+@[^@\s.]+\.[^@\s]{2,}$/.test(email)) return json({ error: "El email no parece correcto." }, 400, cab);
  if (telefono.replace(/\D/g, "").length < 9) return json({ error: "El teléfono no parece correcto." }, 400, cab);
  if (cuerpo.acepta !== true) return json({ error: "Hay que aceptar las condiciones de compra." }, 400, cab);

  let envioCent = 0;
  let direccion = null, cp = null, poblacion = null, provincia = null;
  if (entrega === "envio") {
    if (!envioDisponible) {
      return json({ error: "Ahora mismo solo podemos preparar la recogida en el centro." }, 400, cab);
    }
    envioCent = Number(envioCentConf);
    direccion = txt(c.direccion, 160);
    cp = txt(c.cp, 5);
    poblacion = txt(c.poblacion, 80);
    provincia = txt(c.provincia, 60);
    if (direccion.length < 5) return json({ error: "Falta la dirección." }, 400, cab);
    if (!/^\d{5}$/.test(cp)) return json({ error: "El código postal tiene que ser de 5 cifras." }, 400, cab);
    if (poblacion.length < 2) return json({ error: "Falta la población." }, 400, cab);
    if (provincia.length < 2) return json({ error: "Falta la provincia." }, 400, cab);
  }

  const total = subtotal + envioCent;

  // ---------- freno a los pedidos en cadena ----------
  const ip = (req.headers.get("x-forwarded-for") ?? "").split(",")[0].trim() || null;
  if (ip) {
    const desde = new Date(Date.now() - 10 * 60_000).toISOString();
    const { count } = await db.from("tienda_pedido")
      .select("id", { count: "exact", head: true })
      .eq("ip", ip).gte("creado_en", desde);
    if ((count ?? 0) >= 12) return json({ error: "Demasiados intentos. Prueba dentro de un rato." }, 429, cab);
  }

  // ---------- guardar ----------
  const ref = nuevaReferencia();
  const { data: pedido, error: errPedido } = await db.from("tienda_pedido").insert({
    ref, metodo, subtotal_cent: subtotal, envio_cent: envioCent, total_cent: total,
    entrega, nombre, email, telefono, direccion, cp, poblacion, provincia,
    notas: txt(c.notas, 500) || null, ip,
  }).select("id").single();

  if (errPedido || !pedido) {
    console.error("no se pudo guardar el pedido", errPedido);
    return json({ error: "No se pudo registrar el pedido. Inténtalo otra vez." }, 500, cab);
  }

  const { error: errLineas } = await db.from("tienda_linea")
    .insert(lineas.map((l) => ({ ...l, pedido_id: pedido.id })));
  if (errLineas) {
    console.error("no se pudieron guardar las líneas", errLineas);
    await db.from("tienda_pedido").delete().eq("id", pedido.id);
    return json({ error: "No se pudo registrar el pedido. Inténtalo otra vez." }, 500, cab);
  }

  // ---------- formulario firmado ----------
  const resumen = lineas.map((l) => `${l.unidades}x ${l.nombre}${l.talla !== "U" ? " " + l.talla : ""}`).join(", ");
  const { action, campos } = await formularioCompra(comercio, entorno, {
    numOperacion: ref,
    importeCent: total,
    urlOk: `${web}/pedido/gracias/`,
    urlNok: `${web}/pedido/error/`,
    descripcion: `ABAY ${ref}: ${resumen}`,
    bizum: metodo === "bizum",
  });

  return json({ ok: true, ref, total_cent: total, envio_cent: envioCent, action, campos }, 200, cab);
});

// ---------------------------------------------------------------------
//  Catálogo público: precios, unidades que quedan y coste del envío.
//  No expone ningún dato de clientes ni de pedidos.
// ---------------------------------------------------------------------
async function catalogo(cab: HeadersInit) {
  const db = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    { auth: { persistSession: false } },
  );

  const [{ data: productos }, { data: stock }, { data: ajustes }] = await Promise.all([
    db.from("tienda_producto").select("id, nombre, precio_cent").eq("activo", true),
    db.from("tienda_stock").select("producto_id, talla, unidades"),
    db.from("tienda_ajuste").select("clave, valor"),
  ]);

  const ajuste = (k: string) => ajustes?.find((a) => a.clave === k)?.valor ?? null;
  const envio = ajuste("envio_cent");

  const porId: Record<string, { nombre: string; precio_cent: number }> = {};
  for (const p of productos ?? []) porId[p.id] = { nombre: p.nombre, precio_cent: p.precio_cent };

  const porTalla: Record<string, Record<string, number>> = {};
  for (const s of stock ?? []) {
    if (!porId[s.producto_id]) continue;
    (porTalla[s.producto_id] ??= {})[s.talla] = s.unidades;
  }

  return json({
    ok: true,
    abierto: ajuste("pedidos_abiertos") === "si",
    envio_cent: envio === null || envio === "" ? null : Number(envio),
    envio_texto: ajuste("envio_texto"),
    productos: porId,
    stock: porTalla,
  }, 200, { ...cab, "cache-control": "public, max-age=30" });
}
