for file in *.png; do
    pngquant --ext .png --force 256 "$file"
    optipng "$file"
done
