"""Configuration for yt-dlp-server."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class YtDlpSettings(BaseSettings):
    """
    Settings for yt-dlp.
    This class is generated from the options in `yt_dlp.options.create_parser`.
    It is intended to be used to configure a `yt_dlp.YoutubeDL` instance.
    """

    # General Options
    ignoreerrors: bool | Literal["only_download"] = Field(
        default=False,
        description=(
            "Ignore download and postprocessing errors. "
            "Can be 'only_download' to continue on download errors."
        ),
    )
    use_extractors: list[str] = Field(
        default_factory=list,
        description="Extractor names to use, separated by commas. You can also use regex.",
    )
    default_search: str = Field(
        default="auto",
        description=(
            "Use this prefix for unqualified URLs. E.g. "
            "search_provider:query. Use 'auto' to let yt-dlp guess."
        ),
    )
    flat_playlist: bool | Literal["discard", "discard_in_playlist"] = Field(
        default=False,
        description=(
            "Do not extract the videos of a playlist, only list them. "
            "Can be 'discard' or 'discard_in_playlist'."
        ),
    )
    live_from_start: bool = Field(
        default=False, description="Download livestreams from the start."
    )
    wait_for_video: tuple[float | None, float | None] = Field(
        default=(None, None),
        description=(
            "Wait for scheduled streams to become available. "
            "Optionally specify max wait time in seconds."
        ),
    )
    mark_watched: bool = Field(default=False, description="Mark videos watched")
    no_colors: bool = Field(default=False, description="Do not emit color codes")
    force_colors: bool = Field(default=False, description="Force color codes")
    compat_options: list[str] = Field(
        default_factory=list,
        description="Options that can help keep compatibility with youtube-dl.",
    )

    # Network Options
    proxy: str | None = Field(
        default=None,
        description="Use the specified HTTP/HTTPS/SOCKS proxy.",
    )
    socket_timeout: int = Field(
        default=20,
        description="Time to wait before giving up, in seconds.",
    )
    source_address: str | None = Field(
        default=None,
        description="Client-side IP address to bind to.",
    )
    force_ip: Literal["4", "6"] | None = Field(
        default=None,
        description="Make all connections via IPv4 or IPv6.",
    )
    enable_file_urls: bool = Field(
        default=False,
        description="Enable file:// URLs. May be a security risk.",
    )

    # Geo-restriction
    geo_verification_proxy: str | None = Field(
        default=None,
        description="Use this proxy to verify the IP address for some geo-restricted sites.",
    )
    geo_bypass: bool = Field(
        default=True,
        description="Bypass geographic restriction via faking X-Forwarded-For HTTP header.",
    )
    geo_bypass_country: str | None = Field(
        default=None,
        description="Force bypass geographic restriction with explicitly provided two-letter ISO 3166-2 country code.",
    )
    geo_bypass_ip_block: str | None = Field(
        default=None,
        description="Force bypass geographic restriction with explicitly provided IP block in CIDR notation.",
    )

    # Video Selection
    playlist_items: str = Field(
        default="0",
        description="Comma separated list of playlist items to download.",
    )
    min_filesize: int | None = Field(
        default=None,
        description="Do not download any videos smaller than SIZE (e.g. 50k or 44.6m).",
    )
    max_filesize: int | None = Field(
        default=None,
        description="Do not download any videos larger than SIZE (e.g. 50k or 44.6m).",
    )
    date: str | None = Field(
        default=None,
        description="Download only videos uploaded in this date (YYYYMMDD).",
    )
    datebefore: str | None = Field(
        default=None,
        description="Download only videos uploaded on or before this date (YYYYMMDD).",
    )
    dateafter: str | None = Field(
        default=None,
        description="Download only videos uploaded on or after this date (YYYYMMDD).",
    )
    match_filters: list[str] = Field(
        default_factory=list,
        description="Generic video filter. Specify any key-value pairs to match.",
    )
    break_on_match: bool = Field(
        default=True,
        description="Stop searching for more videos in a playlist after the first match.",
    )
    skip_playlist_after_errors: int = Field(
        default=10,
        description="Number of consecutive download errors after which to skip the rest of the playlist.",
    )
    playlist_reverse: bool = Field(
        default=False,
        description="Download playlist videos in reverse order.",
    )
    playlist_random: bool = Field(
        default=False,
        description="Download playlist videos in random order.",
    )
    subpart: tuple[float | None, float | None] = Field(
        default=(None, None),
        description="Download only a video subpart, e.g., '10:15-15:30'",
    )

    # Download Options
    ratelimit: int | None = Field(
        default=None,
        description="Maximum download rate in bytes per second (e.g. 50K or 4.2M).",
    )
    retries: int | Literal["infinite"] = Field(
        default=10,
        description="Number of retries for transient errors.",
    )
    fragment_retries: int | Literal["infinite"] = Field(
        default=10,
        description="Number of retries for fragments.",
    )
    skip_unavailable_fragments: bool = Field(
        default=True,
        description="Skip unavailable fragments of a video.",
    )
    keepfragments: bool = Field(
        default=False,
        description="Keep downloaded fragments on disk.",
    )
    buffersize: int | None = Field(
        default=1024,
        description="Size of download buffer (e.g. 1024 or 16K).",
    )
    noresizebuffer: bool = Field(
        default=False,
        description="Do not automatically adjust the buffer size.",
    )
    http_chunk_size: int | None = Field(
        default=None,
        description="Size of a chunk for chunk-based HTTP downloading (e.g. 10485760 or 10M).",
    )
    concurrentfragments: int = Field(
        default=1,
        description="Number of fragments of a dash/hlsnative video to download concurrently.",
    )
    external_downloader: str | None = Field(
        default=None,
        description="Name of the external downloader to use.",
    )
    external_downloader_args: str | None = Field(
        default=None,
        description="Arguments to pass to the external downloader.",
    )

    # Filesystem Options
    batchfile: str | None = Field(
        default=None,
        description='File containing URLs to download ("-" for stdin).',
    )
    paths: dict[str, str] = Field(
        default_factory=dict,
        description="The paths where the files are downloaded.",
    )
    outtmpl: str = Field(
        default="",
        description="Output filename template.",
    )
    outtmpl_na_placeholder: str = Field(
        default="NA",
        description="Placeholder for unavailable fields in output template.",
    )
    restrictfilenames: bool = Field(
        default=False,
        description="Restrict filenames to only ASCII characters, and avoid '&' and spaces in filenames.",
    )
    windowsfilenames: bool = Field(
        default=False,
        description="Force filenames to be Windows-compatible.",
    )
    trim_file_name: int = Field(
        default=0,
        description="Limit the filename length (excluding extension).",
    )
    nooverwrites: bool = Field(
        default=False,
        description="Do not overwrite files.",
    )
    continuedl: bool = Field(
        default=True,
        description="Resume partially downloaded files.",
    )
    nopart: bool = Field(
        default=False,
        description="Do not use .part files.",
    )
    updatetime: bool = Field(
        default=True,
        description="Use the Last-modified header to set the file modification time.",
    )
    writedescription: bool = Field(
        default=False,
        description="Write video description to a .description file.",
    )
    writeinfojson: bool = Field(
        default=False,
        description="Write video metadata to a .info.json file.",
    )
    writeannotations: bool = Field(
        default=False,
        description="Write video annotations to a .annotations.xml file.",
    )
    load_info_json: str | None = Field(
        default=None,
        description="JSON file containing the video information.",
    )
    cookiefile: str | None = Field(
        default=None,
        description="File to read cookies from and dump cookie jar in.",
    )
    cookiesfrombrowser: str | None = Field(
        default=None,
        description="The name of the browser to load cookies from.",
    )
    cachedir: str | None = Field(
        default=None,
        description="Location in the filesystem where yt-dlp can store some downloaded information.",
    )

    # Thumbnail Options
    writethumbnail: bool = Field(
        default=False,
        description="Write thumbnail image to disk.",
    )
    write_all_thumbnails: bool = Field(
        default=False,
        description="Write all thumbnail image formats to disk.",
    )

    # Verbosity and Simulation Options
    quiet: bool = Field(
        default=False,
        description="Activate quiet mode.",
    )
    no_warnings: bool = Field(
        default=False,
        description="Ignore warnings.",
    )
    simulate: bool = Field(
        default=False,
        description="Do not download the video and do not write anything to disk.",
    )
    verbose: bool = Field(
        default=False,
        description="Print various debugging information.",
    )
    dumpjson: bool = Field(
        default=False,
        description="Simulate, but print JSON information for each video.",
    )
    dump_single_json: bool = Field(
        default=False,
        description="Simulate, but print JSON information for each video to a single file.",
    )
    print_json: bool = Field(
        default=False,
        description="Be quiet and print the video information as JSON (alias for --quiet --dump-json).",
    )
    print_to_file: dict[str, str] = Field(
        default_factory=dict,
        description="Print given fields to a file.",
    )
    forceprint: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Print given title to stdout.",
    )
    dump_intermediate_pages: bool = Field(
        default=False,
        description="Print downloaded pages encoded using base64.",
    )
    write_intermediate_pages: bool = Field(
        default=False,
        description="Write downloaded intermediary pages to files.",
    )
    debug_printtraffic: bool = Field(
        default=False,
        description="Display sent and read HTTP traffic.",
    )
    call_home: bool = Field(
        default=False,
        description="Contact the yt-dlp server for debugging.",
    )

    # Workarounds
    encoding: str = Field(
        default="utf-8",
        description="Force the specified encoding.",
    )
    no_check_certificate: bool = Field(
        default=False,
        description="Suppress HTTPS certificate validation.",
    )
    prefer_insecure: bool = Field(
        default=False,
        description="Use an unencrypted connection to retrieve information about the video.",
    )
    user_agent: str | None = Field(
        default=None,
        description="Specify a custom user agent.",
    )
    referer: str | None = Field(
        default=None,
        description="Specify a custom referer, use if the video access is restricted to one domain.",
    )
    http_headers: dict[str, str] = Field(
        default_factory=dict,
        description="Specify a custom HTTP header and its value, separated by a colon.",
    )
    bidi_workaround: bool = Field(
        default=False,
        description="Work around terminals that lack bidirectional text support.",
    )
    sleep_requests: float = Field(
        default=0,
        description="Number of seconds to sleep before each request.",
    )
    sleep_interval: float = Field(
        default=0,
        description="Number of seconds to sleep before each download.",
    )
    max_sleep_interval: float = Field(
        default=0,
        description="Maximum number of seconds to sleep.",
    )

    # Video Format Options
    format: str = Field(
        default="bestvideo+bestaudio/best",
        description="Video format code.",
    )
    format_sort: list[str] = Field(
        default_factory=list,
        description="Sort the formats by the given fields.",
    )
    format_sort_force: bool = Field(
        default=False,
        description="Force sorting of formats.",
    )
    video_multistreams: bool = Field(
        default=False,
        description="Allow multiple video streams to be downloaded for each video.",
    )
    audio_multistreams: bool = Field(
        default=False,
        description="Allow multiple audio streams to be downloaded for each video.",
    )
    prefer_free_formats: bool = Field(
        default=False,
        description="Prefer free video formats unless specifically requested.",
    )
    merge_output_format: str | None = Field(
        default=None,
        description="If a merge is required, output to a container of this format.",
    )

    # Subtitle Options
    writesubtitles: bool = Field(
        default=False,
        description="Write subtitle file.",
    )
    writeautomaticsub: bool = Field(
        default=False,
        description="Write automatically generated subtitle file.",
    )
    allsubtitles: bool = Field(
        default=False,
        description="Download all available subtitles.",
    )
    subtitlesformat: str = Field(
        default="best",
        description="Subtitle format.",
    )
    subtitleslangs: list[str] = Field(
        default_factory=list,
        description="Languages of the subtitles to download.",
    )

    # Authentication Options
    username: str | None = Field(
        default=None,
        description="Login with this account ID.",
    )
    password: str | None = Field(
        default=None,
        description="Account password.",
    )
    twofactor: str | None = Field(
        default=None,
        description="Two-factor authentication code.",
    )
    usenetrc: bool = Field(
        default=False,
        description="Use .netrc authentication data.",
    )
    netrc_location: str | None = Field(
        default=None,
        description="Location of the .netrc file.",
    )
    videopassword: str | None = Field(
        default=None,
        description="Video password.",
    )
    ap_mso: str | None = Field(
        default=None,
        description="Adobe Pass multiple-system operator identifier.",
    )
    ap_username: str | None = Field(
        default=None,
        description="Multiple-system operator account login.",
    )
    ap_password: str | None = Field(
        default=None,
        description="Multiple-system operator account password.",
    )
    client_certificate: str | None = Field(
        default=None,
        description="Path to client certificate file.",
    )
    client_certificate_key: str | None = Field(
        default=None,
        description="Path to client certificate key file.",
    )
    client_certificate_password: str | None = Field(
        default=None,
        description="Password for client certificate key.",
    )

    # Post-processing Options
    extractaudio: bool = Field(
        default=False,
        description="Convert video files to audio-only files.",
    )
    audioformat: str | None = Field(
        default=None,
        description="Specify audio format.",
    )
    audioquality: int = Field(
        default=5,
        ge=0,
        le=10,
        description="Specify audio quality, from 0 (best) to 10 (worst).",
    )
    remuxvideo: str | None = Field(
        default=None,
        description="Remux video to another container if necessary.",
    )
    recodevideo: str | None = Field(
        default=None,
        description="Recode video to another format if necessary.",
    )
    postprocessor_args: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Arguments to pass to the postprocessors.",
    )
    keepvideo: bool = Field(
        default=False,
        description="Keep the intermediate video file on disk after post-processing.",
    )
    nopostoverwrites: bool = Field(
        default=False,
        description="Do not overwrite post-processed files.",
    )
    embedsubtitles: bool = Field(
        default=False,
        description="Embed subtitles in the video.",
    )
    embedthumbnail: bool = Field(
        default=False,
        description="Embed thumbnail in the video as cover art.",
    )
    addmetadata: bool = Field(
        default=False,
        description="Embed metadata to the video file.",
    )
    addchapters: bool = Field(
        default=True,
        description="Add chapter markers to the video file.",
    )
    embedinfojson: bool = Field(
        default=False,
        description="Embed the info.json data into the output file.",
    )
    parse_metadata: list[str] = Field(
        default_factory=list,
        description="Parse additional metadata from the video's title.",
    )
    replace_in_metadata: list[str] = Field(
        default_factory=list,
        description="Replace text in metadata fields.",
    )
    xattrs: bool = Field(
        default=False,
        description="Write metadata to the video's xattrs.",
    )
    concat_playlist: Literal["never", "always", "multi_video"] = Field(
        default="never",
        description="Concatenate videos in a playlist.",
    )
    fixup: Literal["never", "warn", "detect_or_warn", "force"] = Field(
        default="detect_or_warn",
        description="Automatically correct known video container issues.",
    )
    ffmpeg_location: str | None = Field(
        default=None,
        description="Location of the ffmpeg/avconv binary.",
    )
    exec: list[str] = Field(
        default_factory=list,
        description="Execute a command on the file after downloading and post-processing.",
    )
    convertsubtitles: str | None = Field(
        default=None,
        description="Convert subtitles to another format.",
    )
    sponsorblock_mark: list[str] = Field(
        default_factory=list,
        description="Mark chapters in the video file for removal.",
    )
    sponsorblock_remove: list[str] = Field(
        default_factory=list,
        description="Remove chapters from the video file.",
    )
    sponsorblock_chapter_title: str = Field(
        default="{category} chapter",
        description="Title template for the sponsor chapters.",
    )
    no_sponsorblock: bool = Field(
        default=False,
        description="Disable SponsorBlock.",
    )
    sponsorblock_api: str = Field(
        default="https://sponsor.ajay.app",
        description="SponsorBlock API location.",
    )
    extractor_retries: int | Literal["infinite"] = Field(
        default=3,
        description="Number of retries for extractors.",
    )
    allow_playlist_files: bool = Field(
        default=True,
        description="Allow downloading of playlist files.",
    )

    # Extractor Options
    extractor_args: dict[str, dict[str, str]] = Field(
        default_factory=dict,
        description="Arguments to pass to the extractors.",
    )
    youtube_include_dash_manifest: bool = Field(
        default=True,
        description="Include DASH manifest in YouTube formats.",
    )
    youtube_include_hls_manifest: bool = Field(
        default=True,
        description="Include HLS manifest in YouTube formats.",
    )

    class Config:
        """Pydantic configuration."""

        env_prefix = "YT_DLP_"
        use_enum_values = True


SETTINGS = YtDlpSettings()
