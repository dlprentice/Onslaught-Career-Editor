/* address: 0x0048ac80 */
/* name: FUN_0048ac80 */
/* signature: undefined FUN_0048ac80(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall FUN_0048ac80(int param_1,undefined4 param_2,undefined4 param_3,float param_4)

{
  uint uVar1;
  void *unaff_ESI;
  void *unaff_EDI;

  CInfantryGuide__SelectNearestTargetReader(param_1);
  uVar1 = Random__NextLCGAbs(DAT_008a9d9c);
  uVar1 = uVar1 & 0x8000ffff;
  if ((int)uVar1 < 0) {
    uVar1 = (uVar1 - 1 | 0xffff0000) + 1;
  }
  param_4 = (float)(int)uVar1 * _DAT_005d8d50 + DAT_00672fd0 + _DAT_005d858c;
  CEventManager__AddEvent_AtTime(&EVENT_MANAGER,2000,unaff_ESI,&param_4,0,(void *)0x0,unaff_EDI);
  return;
}
