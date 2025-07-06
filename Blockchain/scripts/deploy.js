// Archivo: D:\PS\Blockchain\scripts\deploy.js

// Importa los módulos necesarios
const path = require("path");
const fs = require('fs');
const hre = require("hardhat");

async function main() {
  // Obtiene la cuenta que va a desplegar el contrato
  const [deployer] = await hre.ethers.getSigners();
  console.log("Desplegando contratos con la cuenta:", deployer.address);

  // Define la cuenta que será la propietaria del contrato.
  // En nuestro caso, la misma que lo despliega, y que Django usará.
  const initialOwnerAddress = deployer.address;

  // Define los argumentos del constructor del Smart Contract
  const credencialNombre = "Credencial Institucional Digital";
  const credencialSimbolo = "CID";

  // Obtiene la "fábrica" del contrato para poder desplegarlo
  const CredencialAlumno = await hre.ethers.getContractFactory("CredencialAlumno");
  
  // Despliega el contrato en la blockchain
  const credencialAlumno = await CredencialAlumno.deploy(credencialNombre, credencialSimbolo, initialOwnerAddress);

  // Obtiene la dirección del contrato una vez desplegado
  const contractAddress = await credencialAlumno.getAddress();
  console.log("Contrato CredencialAlumno desplegado en:", contractAddress);
  console.log("Owner del contrato (cuenta de Django debería ser esta):", initialOwnerAddress);

  // --- LÓGICA PARA GUARDAR LOS ARCHIVOS PARA DJANGO ---

  // 1. Calcula la ruta de destino
  // Esta ruta sube dos niveles desde /scripts (a /Blockchain y luego a /PS)
  // y luego entra a la carpeta del backend.
  const contractsDir = path.join(__dirname, "..", "..", "backend", "django_project", "blockchain_data");

  // ======================================================================
  //                    ¡LÍNEA DE DEPURACIÓN CLAVE!
  //  Esta línea imprimirá en la consola la ruta exacta que ha calculado.
  // ======================================================================
  console.log("\n[DEBUG] Ruta de destino calculada para los artefactos:", contractsDir, "\n");


  // 2. Asegura que la carpeta de destino exista. Si no, la crea.
  if (!fs.existsSync(contractsDir)) {
      console.log("[DEBUG] La carpeta de destino no existe. Creándola...");
      fs.mkdirSync(contractsDir, { recursive: true });
  }

  // 3. Escribe el archivo con la dirección del contrato
  fs.writeFileSync(
      path.join(contractsDir, "contract-address.json"), // Usamos path.join para más seguridad
      JSON.stringify({ CredencialAlumno: contractAddress }, undefined, 2)
  );
  console.log("Archivo 'contract-address.json' guardado exitosamente.");

  // 4. Obtiene el artefacto completo (que incluye el ABI)
  const CredencialAlumnoArtifact = hre.artifacts.readArtifactSync("CredencialAlumno");

  // 5. Escribe el archivo con el artefacto completo (ABI)
  fs.writeFileSync(
      path.join(contractsDir, "CredencialAlumno.json"), // Usamos path.join de nuevo
      JSON.stringify(CredencialAlumnoArtifact, null, 2)
  );
  console.log("Archivo 'CredencialAlumno.json' (con ABI) guardado exitosamente.");

  console.log("\n¡Puente entre Blockchain y Django configurado!");
}

// Patrón recomendado para manejar la ejecución asíncrona del script
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });