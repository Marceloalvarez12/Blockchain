// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract CredencialAlumno is ERC721, ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;

    event CredencialEmitida(address indexed alumno, uint256 indexed tokenId, string uri);
    event CredencialRevocada(uint256 indexed tokenId);

    constructor(string memory name, string memory symbol, address initialOwner)
        ERC721(name, symbol)
    {
        transferOwnership(initialOwner);
    }

    function _baseURI() internal pure override returns (string memory) {
        return "ipfs://";
    }

    function emitirCredencial(address alumno, string memory uri)
        public
        onlyOwner
        returns (uint256)
    {
        _tokenIdCounter.increment();
        uint256 tokenId = _tokenIdCounter.current();
        _safeMint(alumno, tokenId);
        _setTokenURI(tokenId, uri);
        emit CredencialEmitida(alumno, tokenId, uri);
        return tokenId;
    }

    function revocarCredencial(uint256 tokenId) public onlyOwner {
        require(_exists(tokenId), "CredencialAlumno: El token no existe.");
        _burn(tokenId);
        emit CredencialRevocada(tokenId);
    }

    // Soulbound: no transferible
    function _beforeTokenTransfer(address from, address to, uint256 tokenId, uint256 batchSize)
        internal
        override(ERC721)
    {
        require(from == address(0), "CredencialAlumno: Las credenciales no son transferibles.");
        super._beforeTokenTransfer(from, to, tokenId, batchSize);
    }

    // Requerido por herencia múltiple
    function _burn(uint256 tokenId)
        internal
        override(ERC721, ERC721URIStorage)
    {
        super._burn(tokenId);
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
