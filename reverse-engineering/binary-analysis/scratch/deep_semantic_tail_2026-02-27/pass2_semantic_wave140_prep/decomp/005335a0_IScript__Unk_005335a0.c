/* address: 0x005335a0 */
/* name: IScript__Unk_005335a0 */
/* signature: void __fastcall IScript__Unk_005335a0(int param_1) */


void __fastcall IScript__Unk_005335a0(int param_1)

{
  if (DAT_008a9ac0 == 4) {
    CScriptObjectCode__Reset();
    return;
  }
  CScriptObjectCode__CallEvent(*(undefined4 *)(param_1 + 0xc),6,&DAT_0089c528,0);
  return;
}
