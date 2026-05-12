```bash
bundle exec jekyll serve
```

If libraries are missing or it is the first time install:
* install Ruby with rbenv

```bash
bundle config set path vendor/bundle
bundle install
bundle exec jekyll serve
```

or

```bash
gem pristine --all
bundle install
bundle exec jekyll serve
```

If the environment is still broken:
```bash
rm -rf vendor/bundle .bundle
rm -f Gemfile.lock
bundle add webrick
bundle install
bundle exec jekyll serve
```