// scripts/deploy.ts
import { ethers } from "hardhat";

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Desplegando el contrato con la cuenta:", deployer.address);

  const RegistryFactory = await ethers.getContractFactory("CredencialRegistry");
  const registry = await RegistryFactory.deploy(deployer.address);

  // En v2, se usa .deployed() para esperar a que la transacción se mine.
  await registry.deployed();

  console.log(`Contrato 'CredencialRegistry' desplegado en: ${registry.address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});