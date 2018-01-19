# pythoncad-optimizer (pyocad)

Python optimizer for circuit design and optimization using Cadence Virtuoso

## Usage

1. Place the packages **cadence/** and **server/** in the machine that runs Cadence (i.e. the **server**).
2. Place the package **opycad/** in your computer.
3. Connect your computer to **server** through ssh using local port forwarding for the port specified in the file *config.yaml*. Ex:

```Shell script
ssh -L LOCAL_PORT:localhost:HOST_PORT user@SERVER_IP
```

4. Run Cadence, in the **server**, through the script *run_cadence.sh*.
5. Run *opycad.py* in your computer.

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## Versioning

TODO: Write history

## Authors

* **Miguel Fernandes** - *Initial work* - [mdmfernandes](https://github.com/mdmfernandes)

## Credits

TODO: Write credits

## License

TODO: Write license

## Acknowledgments

TODO: Write acknowledgments