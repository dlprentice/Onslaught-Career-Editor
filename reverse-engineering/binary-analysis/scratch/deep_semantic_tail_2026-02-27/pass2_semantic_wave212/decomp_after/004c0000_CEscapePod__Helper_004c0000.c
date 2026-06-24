/* address: 0x004c0000 */
/* name: CEscapePod__Helper_004c0000 */
/* signature: void __fastcall CEscapePod__Helper_004c0000(void * param_1) */


void __fastcall CEscapePod__Helper_004c0000(void *param_1)

{
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d4028;
  pvStack_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &pvStack_c;
  CParticleManager__RemoveFromGlobalList();
  local_4 = 0xffffffff;
  CActor__ctor_like_004013d0(param_1);
  ExceptionList = pvStack_c;
  return;
}
