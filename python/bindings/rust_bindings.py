try:
    import goat_ts_core
except ImportError:
    import warnings
    warnings.warn("Rust extension not built; using dummy. Run: maturin develop --manifest-path=rust/Cargo.toml")
    class Dummy:
        pass
    goat_ts_core = Dummy()
