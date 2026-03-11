try:
    import goat_ts_core
except ImportError:
    # Extension not built; use dummy. Status is shown in the app (Setup step) or run: maturin develop --manifest-path=rust/Cargo.toml
    class Dummy:
        pass
    goat_ts_core = Dummy()
