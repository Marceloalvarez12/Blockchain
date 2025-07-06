require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config(); // Si usas .env para claves privadas de testnet

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.28",
  networks: {
    hardhat: { // Red local por defecto para desarrollo rápido
      // chainId: 1337 // Puedes configurar esto si es necesario
    },
    // Ejemplo para Sepolia Testnet (necesitarás RPC URL y Private Key)
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL || "",
      accounts: process.env.PRIVATE_KEY_DJANGO_WALLET !== undefined ? [process.env.PRIVATE_KEY_DJANGO_WALLET] : [],
    }
  },
  // ... otras configuraciones como etherscan para verificación
};