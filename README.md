# pythoncad-optimizer (pyocad)

Python optimizer for circuit design and optimization using Cadence Virtuoso

## Usage

* Place the folders **cadence** and **server** in the machine that runs Cadence (i.e. the **server**).

* Place the folder **opycad** in your computer.

* Connect your computer to **server** through ssh using local port forwarding for the port specified in the file *config.yaml*. Ex:

```Shell script
ssh -L LOCAL_PORT:localhost:HOST_PORT user@SERVER_IP
```

* Start Cadence, in the **server**, through command line using the command below. Note that `$CADENCE_FOLDER` refers to the folder **cadence** of the project.

```Shell script
icfb -nograph -restore $CADENCE_FOLDER/cadence.il
```

* Start *opycad.py* in your computer.

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