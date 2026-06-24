/* address: 0x00533660 */
/* name: IScript__CallEventId5_OrReset */
/* signature: void __fastcall IScript__CallEventId5_OrReset(int param_1) */


void __fastcall IScript__CallEventId5_OrReset(int param_1)

{
  if (DAT_008a9ac0 == 4) {
    CScriptObjectCode__Reset();
    return;
  }
  CScriptObjectCode__CallEvent(*(undefined4 *)(param_1 + 0xc),5,&DAT_0089c528,0);
  return;
}
