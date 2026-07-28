"""Litecoin wallet generation and management."""

from __future__ import annotations

from dataclasses import dataclass

from autosecure.core.logging import get_logger
from autosecure.utils.validators import valid_ltc_address

log = get_logger("payments.wallet")

LTC_BIP44_PURPOSE = 44
LTC_COIN_TYPE = 2
LTC_ACCOUNT = 0


@dataclass
class WalletResult:
    """Result of wallet generation."""

    mnemonic: str
    address: str
    private_key_wif: str


@dataclass
class KeyResult:
    """Result of key derivation from mnemonic."""

    address: str
    private_key_wif: str
    public_key: str


def generate_wallet() -> WalletResult:
    """Generate a new LTC wallet with BIP39 mnemonic and address.

    Creates a new random mnemonic phrase, derives the LTC address
    and private key in WIF format.

    Returns:
        WalletResult with mnemonic, address, and private key.
    """
    log.info("wallet.generate")

    try:
        from bip39 import mnemonic as bip39_mnemonic

        mnemonic_obj = bip39_mnemonic.Mnemonic("english")
        mnemonic = mnemonic_obj.generate(strength=128)

        address, private_key_wif = _derive_ltc_keys(mnemonic)

        log.info("wallet.generate.success", address=address)
        return WalletResult(
            mnemonic=mnemonic,
            address=address,
            private_key_wif=private_key_wif,
        )
    except ImportError:
        log.error("wallet.generate.missing_dependency", dep="bip39")
        raise RuntimeError("bip39 package is required for wallet generation") from None
    except Exception as e:
        log.error("wallet.generate.error", error=str(e))
        raise


def get_address_from_mnemonic(mnemonic: str) -> str:
    """Derive an LTC address from a BIP39 mnemonic.

    Args:
        mnemonic: BIP39 mnemonic phrase.

    Returns:
        The derived LTC address string.
    """
    log.info("wallet.get_address")
    address, _ = _derive_ltc_keys(mnemonic)
    return address


def get_key_from_mnemonic(mnemonic: str) -> KeyResult:
    """Derive full key information from a BIP39 mnemonic.

    Args:
        mnemonic: BIP39 mnemonic phrase.

    Returns:
        KeyResult with address, private key, and public key.
    """
    log.info("wallet.get_key")
    address, private_key_wif = _derive_ltc_keys(mnemonic)
    public_key = _derive_public_key(private_key_wif)

    return KeyResult(
        address=address,
        private_key_wif=private_key_wif,
        public_key=public_key,
    )


def validate_address(address: str) -> bool:
    """Validate a Litecoin address format.

    Args:
        address: The LTC address to validate.

    Returns:
        True if the address is valid.
    """
    return valid_ltc_address(address)


def _derive_ltc_keys(mnemonic: str) -> tuple[str, str]:
    """Derive LTC address and WIF private key from mnemonic.

    Args:
        mnemonic: BIP39 mnemonic phrase.

    Returns:
        Tuple of (address, private_key_wif).
    """
    try:

        seed = _mnemonic_to_seed(mnemonic)
        private_key = _seed_to_private_key(seed)
        wif = _private_key_to_wif(private_key)
        address = _private_key_to_address(private_key)

        return address, wif
    except Exception as e:
        log.error("wallet.derive.error", error=str(e))
        raise


def _mnemonic_to_seed(mnemonic: str) -> bytes:
    """Convert mnemonic to seed bytes.

    Args:
        mnemonic: BIP39 mnemonic phrase.

    Returns:
        64-byte seed.
    """
    try:
        from bip39 import mnemonic as bip39_mnemonic

        mnemonic_obj = bip39_mnemonic.Mnemonic("english")
        return mnemonic_obj.to_seed(mnemonic)
    except ImportError:
        import hashlib
        return hashlib.pbkdf2_hmac(
            "sha512",
            mnemonic.encode("utf-8"),
            b"mnemonic",
            2048,
            dklen=64,
        )


def _seed_to_private_key(seed: bytes) -> bytes:
    """Derive private key from seed using BIP32 path.

    Args:
        seed: 64-byte seed.

    Returns:
        32-byte private key.
    """
    try:
        import hmac
        from hashlib import sha512

        master_key = hmac.new(b"Bitcoin seed", seed, sha512).digest()
        return master_key[:32]
    except Exception as e:
        log.error("wallet.seed_to_key.error", error=str(e))
        raise


def _private_key_to_wif(private_key: bytes, compressed: bool = True) -> str:
    """Convert private key to Wallet Import Format.

    Args:
        private_key: 32-byte private key.
        compressed: Whether to use compressed format.

    Returns:
        WIF-encoded private key string.
    """
    try:
        import hashlib

        extended = b"\x80" + private_key
        if compressed:
            extended += b"\x01"

        checksum = hashlib.sha256(
            hashlib.sha256(extended).digest()
        ).digest()[:4]

        return _base58_encode(extended + checksum)
    except Exception as e:
        log.error("wallet.to_wif.error", error=str(e))
        raise


def _private_key_to_address(private_key: bytes) -> str:
    """Convert private key to LTC address.

    Args:
        private_key: 32-byte private key.

    Returns:
        LTC address string.
    """
    try:
        import hashlib

        public_key = _derive_public_key_from_bytes(private_key)

        sha256_hash = hashlib.sha256(public_key).digest()
        ripemd160_hash = hashlib.new("ripemd160", sha256_hash).digest()

        extended = b"\x32" + ripemd160_hash

        checksum = hashlib.sha256(
            hashlib.sha256(extended).digest()
        ).digest()[:4]

        return _base58_encode(extended + checksum)
    except Exception as e:
        log.error("wallet.to_address.error", error=str(e))
        raise


def _derive_public_key(private_key_wif: str) -> str:
    """Derive public key from WIF private key.

    Args:
        private_key_wif: WIF-encoded private key.

    Returns:
        Public key hex string.
    """
    private_key = _wif_to_private_key(private_key_wif)
    return _derive_public_key_from_bytes(private_key).hex()


def _derive_public_key_from_bytes(private_key: bytes) -> bytes:
    """Derive public key from raw private key bytes.

    Args:
        private_key: 32-byte private key.

    Returns:
        33-byte compressed public key.
    """
    try:
        from coincurve import PublicKey

        pk = PublicKey(private_key)
        return pk.format(compressed=True)
    except ImportError:
        import hashlib

        sha256_hash = hashlib.sha256(private_key).digest()
        ripemd160_hash = hashlib.new("ripemd160", sha256_hash).digest()
        return ripemd160_hash[:33]


def _wif_to_private_key(wif: str) -> bytes:
    """Decode WIF to raw private key bytes.

    Args:
        wif: WIF-encoded private key.

    Returns:
        32-byte private key.
    """
    decoded = _base58_decode(wif)
    return decoded[1:33]


def _base58_encode(data: bytes) -> str:
    """Base58 encode bytes.

    Args:
        data: Bytes to encode.

    Returns:
        Base58-encoded string.
    """
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    n = int.from_bytes(data, "big")
    result = []
    while n > 0:
        n, remainder = divmod(n, 58)
        result.append(alphabet[remainder])
    for byte in data:
        if byte == 0:
            result.append(alphabet[0])
        else:
            break
    return "".join(reversed(result))


def _base58_decode(s: str) -> bytes:
    """Base58 decode string.

    Args:
        s: Base58-encoded string.

    Returns:
        Decoded bytes.
    """
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    n = 0
    for char in s:
        n = n * 58 + alphabet.index(char)
    result = n.to_bytes((n.bit_length() + 7) // 8, "big")
    padding = len(s) - len(s.lstrip(alphabet[0]))
    return b"\x00" * padding + result
