<TESTCASE_BEGIN>
<TESTCASE_HEADER_BEGIN>
    <TITLE>      "执行用例自动化生成脚本"
    <INDEX>      "执行编号"
    <LEVEL>      "2"
    <WEIGHT>     "4"
    <MODULE>     "no_modename"
    <TYPE>       "FUN"
    <AUTHOR>     "Automatic Generation"
    <LIMITATION> "CmwV7Device"
    <VERSION> "2.1"
    <DESIGN> "log自动化脚本"
    <SOURCE> "no_topo_name"
<TESTCASE_HEADER_END>

<TESTCASE_DEVICE_MAP_BEGIN>

<TESTCASE_DEVICE_MAP_END>

<STEP> "step 1" {
  DUT1 Config "

      save mirror.cfg
      reset logbuffer
      ####start####	"

	<CHECK> description "check 1"
	<CHECK> type custom
	<CHECK> args  {  
	    DUT1 Config "return"
	    DUT1 CheckConfig -command "display this" -include "sss"  -checkreturn configreturn
    }
	<CHECK> repeat 1 -interval 5 
    <CHECK> whenfailed {PUTSINFO "$configreturn"}
    <CHECK> 
}
<TESTCASE_END>