// =====================================================================
//  TPV Virtual de Cecabank — cálculo de firmas (manual 8.21)
//
//  Firma de la petición de compra (Cifrado = SHA2):
//    clave + MerchantID + AcquirerBIN + TerminalID + Num_operacion +
//    Importe + TipoMoneda + Exponente + Referencia + Cifrado +
//    URL_OK + URL_NOK + Exencion_SCA + fechaTope
//
//  Firma del aviso on-line que manda Cecabank:
//    clave + MerchantID + AcquirerBIN + TerminalID + Num_operacion +
//    Importe + TipoMoneda + Exponente + Referencia
//  (en el aviso, el Importe va relleno con ceros a la izquierda hasta 12)
//
//  SHA-256, resultado en hexadecimal en minúsculas.
// =====================================================================

export const ENTORNOS = {
  pruebas:    "https://tpv.ceca.es/tpvweb/tpv/compra.action",
  produccion: "https://pgw.ceca.es/tpvweb/tpv/compra.action",
} as const;

export type Entorno = keyof typeof ENTORNOS;

export interface Comercio {
  clave: string;        // clave de cifrado — SOLO como secreto del servidor
  merchantId: string;   // 9
  acquirerBin: string;  // 10
  terminalId: string;   // 8
}

export async function sha256hex(cadena: string): Promise<string> {
  const datos = new TextEncoder().encode(cadena);
  const hash = await crypto.subtle.digest("SHA-256", datos);
  return Array.from(new Uint8Array(hash))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export interface Compra {
  numOperacion: string;
  importeCent: number;     // entero, en céntimos
  urlOk: string;
  urlNok: string;
  descripcion?: string;
  idioma?: string;         // 1 = español, 4 = gallego
  bizum?: boolean;         // va directo a Bizum sin pasar por la pantalla de tarjeta
}

/** Devuelve el ACTION y los campos ocultos del formulario que hay que enviar al TPV. */
export async function formularioCompra(
  c: Comercio,
  entorno: Entorno,
  compra: Compra,
): Promise<{ action: string; campos: Record<string, string> }> {
  const importe = String(Math.round(compra.importeCent));
  const tipoMoneda = "978";
  const exponente = "2";
  const cifrado = "SHA2";
  const referencia = "";
  const exencionSca = "";
  const fechaTope = "";

  const cadena =
    c.clave + c.merchantId + c.acquirerBin + c.terminalId +
    compra.numOperacion + importe + tipoMoneda + exponente +
    referencia + cifrado + compra.urlOk + compra.urlNok +
    exencionSca + fechaTope;

  const campos: Record<string, string> = {
    MerchantID: c.merchantId,
    AcquirerBIN: c.acquirerBin,
    TerminalID: c.terminalId,
    Num_operacion: compra.numOperacion,
    Importe: importe,
    TipoMoneda: tipoMoneda,
    Exponente: exponente,
    URL_OK: compra.urlOk,
    URL_NOK: compra.urlNok,
    Pago_soportado: "SSL",
    Cifrado: cifrado,
    Idioma: compra.idioma ?? "1",
    Firma: await sha256hex(cadena),
  };
  if (compra.descripcion) campos.Descripcion = compra.descripcion.slice(0, 200);
  if (compra.bizum) campos.inicioBizum = "1";

  return { action: ENTORNOS[entorno], campos };
}

/** Comprueba la firma del aviso on-line. Tolera que el Importe venga o no relleno de ceros. */
export async function avisoEsAutentico(
  c: Comercio,
  datos: Record<string, string>,
): Promise<boolean> {
  const recibida = (datos.Firma ?? "").trim().toLowerCase();
  if (!/^[0-9a-f]{64}$/.test(recibida)) return false;

  const importe = (datos.Importe ?? "").trim();
  const variantes = new Set([
    importe,
    importe.padStart(12, "0"),
    importe.replace(/^0+/, "") || "0",
  ]);

  for (const imp of variantes) {
    const cadena =
      c.clave + (datos.MerchantID ?? "") + (datos.AcquirerBIN ?? "") +
      (datos.TerminalID ?? "") + (datos.Num_operacion ?? "") + imp +
      (datos.TipoMoneda ?? "") + (datos.Exponente ?? "") + (datos.Referencia ?? "");
    if (iguales(await sha256hex(cadena), recibida)) return true;
  }
  return false;
}

/** Comparación en tiempo constante, para no filtrar nada por el tiempo de respuesta. */
function iguales(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let dif = 0;
  for (let i = 0; i < a.length; i++) dif |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return dif === 0;
}

/** Referencia del pedido: única, corta y sin caracteres raros (el TPV los prohíbe). */
export function nuevaReferencia(): string {
  const ahora = new Date();
  const dia =
    String(ahora.getUTCFullYear()).slice(2) +
    String(ahora.getUTCMonth() + 1).padStart(2, "0") +
    String(ahora.getUTCDate()).padStart(2, "0");
  const letras = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  const azar = Array.from(crypto.getRandomValues(new Uint8Array(6)))
    .map((n) => letras[n % letras.length]).join("");
  return "A" + dia + azar;          // p.ej. A261105KQ7F2M
}
