/* address: 0x004a4310 */
/* name: FUN_004a4310 */
/* signature: undefined FUN_004a4310(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall FUN_004a4310(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  uint uVar2;
  float10 extraout_ST0;
  float10 fVar3;
  undefined4 uStack_8;

  uVar2 = 0xffffffff;
  if (DAT_00704a88 != '\0') {
    PLATFORM__GetSysTimeFloat();
    CDXTexture__Unk_0055e3ea();
    fVar3 = (float10)fcos(extraout_ST0 * (float10)_DAT_005d85e0);
    uStack_8 = (int)(longlong)
                    ROUND((fVar3 + (float10)_DAT_005d8568) * (float10)_DAT_005d85ec *
                          (float10)_DAT_005d8c70);
    uVar2 = 0xff - uStack_8;
    uVar2 = ((uVar2 | 0xffffff00) << 8 | uVar2) << 8 | uVar2;
  }
  uVar1 = (**(code **)(*param_1 + 8))();
  CMenuItem__Render(param_2,param_3,param_4,uVar2,uVar1);
  return;
}
