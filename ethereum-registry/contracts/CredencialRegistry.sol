// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Importamos el contrato 'Ownable' de OpenZeppelin.
// Nos da un sistema de permisos simple donde solo una cuenta (el "owner")
// puede ejecutar ciertas funciones.
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title CredencialRegistry
 * @dev Este contrato actúa como un registro público y verificable para anclar
 * el estado de las credenciales digitales emitidas en un sistema externo (como Hyperledger Fabric).
 * No almacena los detalles de la credencial, solo un hash único y su estado de validez.
 */
contract CredencialRegistry is Ownable {

    // --- State Variables ---

    // Este es el registro principal. Es un mapeo (como un diccionario o tabla hash)
    // que asocia un hash de 32 bytes (el 'credencialHash') a un valor booleano (true si es válida, false si no).
    // Es 'public' para que cualquiera pueda consultarlo gratuitamente.
    mapping(bytes32 => bool) public credencialesValidas;

    // --- Events ---

    // Se emite un evento cada vez que una nueva credencial es anclada.
    // Los servicios externos pueden "escuchar" estos eventos.
    // 'indexed' permite buscar y filtrar eventos por este parámetro.
    event CredencialAnclada(bytes32 indexed credencialHash);

    // Se emite un evento cuando una credencial es revocada.
    event CredencialRevocada(bytes32 indexed credencialHash);


    // --- Constructor ---

    /**
     * @dev El constructor se ejecuta una sola vez, cuando el contrato es desplegado.
     * Establece la cuenta que despliega el contrato como el 'owner' inicial.
     * @param initialOwner La dirección de la cuenta que tendrá los permisos de administrador.
     */
    constructor(address initialOwner) Ownable(initialOwner) {}


    // --- Functions ---

    /**
     * @dev Ancla el hash de una nueva credencial en la blockchain, marcándola como válida.
     * Esta función solo puede ser llamada por el 'owner' del contrato (nuestra API Gateway).
     * @param credencialHash El hash SHA-256 único de los datos de la credencial.
     */
    function anclarCredencial(bytes32 credencialHash) public onlyOwner {
        // Requisito: El hash no debe existir previamente en el registro.
        require(!credencialesValidas[credencialHash], "CredencialRegistry: La credencial ya fue anclada previamente.");

        // Se marca el hash como válido (true).
        credencialesValidas[credencialHash] = true;

        // Se emite el evento para notificar al mundo.
        emit CredencialAnclada(credencialHash);
    }

    /**
     * @dev Revoca una credencial existente, marcándola como inválida.
     * Esta función también solo puede ser llamada por el 'owner'.
     * @param credencialHash El hash de la credencial a revocar.
     */
    function revocarCredencial(bytes32 credencialHash) public onlyOwner {
        // Requisito: El hash debe existir y estar como válido.
        require(credencialesValidas[credencialHash], "CredencialRegistry: La credencial no existe o ya fue revocada.");

        // Se marca el hash como inválido (false).
        credencialesValidas[credencialHash] = false;

        // Se emite el evento de revocación.
        emit CredencialRevocada(credencialHash);
    }
}