/* address: 0x0042d300 */
/* name: OptionsEntries__InitSentinelEntry */
/* signature: void __fastcall OptionsEntries__InitSentinelEntry(void * this) */


void __fastcall OptionsEntries__InitSentinelEntry(void *this)

{
  *(undefined1 *)this = 0;
  *(undefined4 *)((int)this + 4) = 0xffffffff;
  return;
}
