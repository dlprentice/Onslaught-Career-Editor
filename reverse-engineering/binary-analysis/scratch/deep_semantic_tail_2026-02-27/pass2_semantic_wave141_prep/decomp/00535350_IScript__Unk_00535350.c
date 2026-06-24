/* address: 0x00535350 */
/* name: IScript__Unk_00535350 */
/* signature: void __fastcall IScript__Unk_00535350(void * param_1) */


void __fastcall IScript__Unk_00535350(void *param_1)

{
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d7028;
  local_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &local_c;
  CScriptObjectCode__ClearStack();
  local_4 = 0xffffffff;
  CMonitor__Shutdown(param_1);
  ExceptionList = local_c;
  return;
}
