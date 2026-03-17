from whitenoise.storage import CompressedManifestStaticFilesStorage, MissingFileError


class PatchedStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """
    Extends CompressedManifestStaticFilesStorage to skip missing files.
    Required for Django 6.0 compatibility — some SVG references in
    admin CSS do not exist physically.
    """

    manifest_strict = False

    def post_process(self, paths, dry_run=False, **options):
        try:
            yield from super().post_process(paths, dry_run, **options)
        except MissingFileError:
            pass