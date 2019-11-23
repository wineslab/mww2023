sudo add-apt-repository -y ppa:ettusresearch/uhd
sudo add-apt-repository -y ppa:johnsond-u/sdr
sudo apt-get update

for thing in $*
do
    case $thing in
        gnuradio)
            sudo DEBIAN_FRONTEND=noninteractive apt-get install -y gnuradio python3-gi gobject-introspection gir1.2-gtk-3.0 python3-cairo python3-gi-cairo
            ;;

        srslte)
            sudo DEBIAN_FRONTEND=noninteractive apt-get install -y srslte
            ;;
    esac
done

sudo "/usr/lib/uhd/utils/uhd_images_downloader.py"
