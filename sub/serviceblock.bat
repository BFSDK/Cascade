exit /b 0

:: DEBOUNCE SERVICE BLOCK
:: Do not edit this block.

:: String length
:_std_str_len
setlocal enabledelayedexpansion
set "str=!%~1!"
set "length=0"

if not defined str (
    endlocal & set "%~2=0"
    exit /b 0
)

:_std_str_len_loop
if defined str (
    set "str=!str:~1!"
    set /a "length+=1"
    goto :_std_str_len_loop
)

endlocal & set "%~2=%length%"
exit /b 0

:: String UPPER
:_std_str_upper
setlocal enabledelayedexpansion
set "str=!%~1!"

if not defined str (
    endlocal & set "%~2="
    exit /b 0
)

for %%a in (
    a:A b:B c:C d:D e:E f:F g:G h:H i:I j:J k:K l:L m:M n:N o:O p:P q:Q r:R s:S t:T u:U v:V w:W x:X y:Y z:Z а:А б:Б в:В г:Г д:Д е:Е ё:Ё ж:Ж з:З и:И й:Й к:К л:Л м:М н:Н о:О п:П р:Р с:С т:Т у:У ф:Ф х:Х ц:Ц ч:Ч ш:Ш щ:Щ ъ:Ъ ы:Ы ь:Ь э:Э ю:Ю я:Я є:Є і:І ї:Ї ґ:Ґ ў:Ў š:Š č:Č ž:Ž ć:Ć đ:Đ ł:Ł ą:Ą ę:Ę ś:Ś ź:Ź ż:Ż ń:Ń ť:Ť ď:Ď ň:Ň ĺ:Ĺ ľ:Ľ ŕ:Ŕ ě:Ě ů:Ů ű:Ű ős:ŐS ő:Ő ğ:Ğ ı:I ş:Ş ä:Ä ö:Ö ü:Ü é:É è:È ê:Ê à:À â:Â ç:Ç ñ:Ñ ó:Ó ò:Ò ô:Ô á:Á å:Å æ:Æ ø:Ø ß:SS
) do (
    for /f "tokens=1,2 delims=:" %%i in ("%%a") do (
        set "str=!str:%%i=%%j!"
    )
)

endlocal & set "%~2=%str%"
exit /b 0

:: String lower
:_std_str_lower
setlocal enabledelayedexpansion
set "str=!%~1!"

if not defined str (
    endlocal & set "%~2="
    exit /b 0
)

for %%a in (
    A:a B:b C:c D:d E:e F:f G:g H:h I:i J:j K:k L:l M:m N:n O:o P:p Q:q R:r S:s T:t U:u V:v W:w X:x Y:y Z:z
    А:а Б:б В:в Г:г Д:д Е:е Ё:ё Ж:ж З:з И:и Й:й К:к Л:л М:м Н:н О:о П:п Р:р С:с Т:т У:у Ф:ф Х:х Ц:ц Ч:ч Ш:ш Щ:щ Ъ:ъ Ы:ы Ь:ь Э:э Ю:ю Я:я
    Є:є І:і Ї:ї Ґ:ґ Ў:ў
    Š:š Č:č Ž:ž Ć:ć Đ:đ Ł:ł Ą:ą Ę:ę Ś:ś Ź:ź Ż:ż Ń:ń Ť:ť Ď:ď Ň:ň Ĺ:ĺ Ľ:ľ Ŕ:ŕ Ě:ě Ů:ů Ű:ű Ő:ő Ğ:ğ I:ı Ş:ş
    Ä:ä Ö:ö Ü:ü É:é È:è Ê:ê À:à Â:â Ç:ç Ñ:ñ Ó:ó Ò:ò Ô:ô Á:á Å:å Æ:æ Ø:ø
) do (
    for /f "tokens=1,2 delims=:" %%i in ("%%a") do (
        set "str=!str:%%i=%%j!"
    )
)

endlocal & set "%~2=%str%"
exit /b 0

:: String trim
:_std_str_trim
setlocal enabledelayedexpansion
set "str=!%~1!"
:_std_str_trim_left
if "!str:~0,1!"==" " set "str=!str:~1!" & goto :_std_str_trim_left
:_std_str_trim_right
if "!str:~-1!"==" " set "str=!str:~0,-1!" & goto :_std_str_trim_right
endlocal & set "%~2=%str%"
exit /b 0

:: String contains (?)
:_std_str_contains
setlocal enabledelayedexpansion
set "str=!%~1!"
set "sub=%~2"
if not "!str:%sub%=!"=="!str!" (
    endlocal & set "%~3=1"
) else (
    endlocal & set "%~3=0"
)
exit /b 0

:: Array append
:_std_arr_append
setlocal enabledelayedexpansion
set "arr_name=%~1"
set "val=%~2"

set "curr_len=!%arr_name%_len!"
if not defined curr_len set "curr_len=0"

endlocal & (
    set "%~1_%curr_len%=%~2"
    set /a "%~1_len=%curr_len%+1"
)
exit /b 0

:: Array length
:_std_arr_len
setlocal enabledelayedexpansion
set "arr_name=%~1"

set "curr_len=!%arr_name%_len!"
if not defined curr_len set "curr_len=0"

endlocal & set "%~2=%curr_len%"
exit /b 0