// Comprueba que calculamos la firma igual que el manual 8.21 de Cecabank.
// node prueba-firma.mjs
import { createHash } from "node:crypto";
const sha = (s) => createHash("sha256").update(s, "utf8").digest("hex");

const casos = [
  ["SHA-256 básico", sha("El coche amarillo"),
   "91a736731a4281666fa562ed7eb5e7dbe451f92c7d973c307bc060959d6b1012"],
  ["firma de compra (SHA2)",
   sha("99888888" + "111950028" + "0000554052" + "00000003" + "123" + "500" +
       "978" + "2" + "" + "SHA2" + "http://www.ceca.es" + "http://www.ceca.es" + "" + ""),
   "2b7f686593f1a424c510321e4bc354d21924e02e980a90f4d46c41f92a06f5a9"],
  ["firma de compra (SHA2-1, con descripción)",
   sha("99888888" + "111950028" + "0000554052" + "00000003" + "123" + "500" +
       "978" + "2" + "" + "SHA2" + "http://www.ceca.es" + "http://www.ceca.es" +
       "Esta es la descripcion"),
   "e87e737f9287984bfdc213ee27b3f5366692d661998109bf096e77e97ea49fa2"],
];

let fallos = 0;
for (const [nombre, obtenido, esperado] of casos) {
  const bien = obtenido === esperado;
  if (!bien) fallos++;
  console.log(`${bien ? "OK  " : "MAL "} ${nombre}`);
  if (!bien) console.log(`     esperado ${esperado}\n     obtenido ${obtenido}`);
}
process.exit(fallos ? 1 : 0);
