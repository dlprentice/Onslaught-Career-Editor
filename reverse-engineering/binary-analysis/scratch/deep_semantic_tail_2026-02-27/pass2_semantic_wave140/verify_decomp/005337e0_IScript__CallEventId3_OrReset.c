/* address: 0x005337e0 */
/* name: IScript__CallEventId3_OrReset */
/* signature: void __fastcall IScript__CallEventId3_OrReset(int param_1) */


void __fastcall IScript__CallEventId3_OrReset(int param_1)

{
  if (DAT_008a9ac0 == 4) {
    CScriptObjectCode__Reset();
    return;
  }
  CScriptObjectCode__CallEvent(*(undefined4 *)(param_1 + 0xc),3,&DAT_0089c528,0);
  return;
}
