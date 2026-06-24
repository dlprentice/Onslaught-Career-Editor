/* address: 0x0044d390 */
/* name: CFEPSaveGame__InitDialogAndLayoutState */
/* signature: int CFEPSaveGame__InitDialogAndLayoutState(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFEPSaveGame__InitDialogAndLayoutState(void)

{
  int iVar1;
  float fVar2;
  int in_EAX;
  int iVar3;
  void *pvVar4;
  void *pvVar5;
  int in_ECX;
  undefined4 in_stack_00000004;
  undefined4 in_stack_00000008;
  float in_stack_0000000c;
  undefined4 in_stack_00000010;
  void *in_stack_00000014;
  int in_stack_00000018;
  uint in_stack_0000001c;
  uint in_stack_00000020;
  undefined4 in_stack_00000024;
  int in_stack_00000028;
  undefined4 in_stack_0000002c;

  if (*(int *)(in_ECX + 0x1f8c) != 0) {
    return in_EAX;
  }
  *(undefined4 *)(in_ECX + 4) = in_stack_00000004;
  *(undefined4 *)(in_ECX + 0x1fa0) = 0xffffffff;
  *(undefined4 *)(in_ECX + 0x1fa4) = 0xffffffff;
  *(undefined4 *)(in_ECX + 8) = in_stack_00000008;
  *(float *)(in_ECX + 0x1f84) = (float)in_stack_0000001c;
  *(undefined4 *)(in_ECX + 0x1f90) = in_stack_00000024;
  *(float *)(in_ECX + 0xc) = in_stack_0000000c;
  *(float *)(in_ECX + 0x1f78) = (float)in_stack_00000020;
  *(int *)(in_ECX + 0x1f5c) = in_stack_00000018;
  *(int *)(in_ECX + 0x1f98) = in_stack_00000028;
  *(undefined4 *)(in_ECX + 0x1f94) = 0;
  *(undefined4 *)(in_ECX + 0x14) = in_stack_00000010;
  *(undefined4 *)(in_ECX + 0x1f9c) = in_stack_0000002c;
  *(undefined4 *)(in_ECX + 0x1f88) = 0;
  *(undefined4 *)(in_ECX + 0x1f7c) = 0;
  *(undefined4 *)(in_ECX + 0x1f80) = 0;
  if (in_stack_00000020 == 0) {
    *(undefined4 *)(in_ECX + 0x1f80) = 1;
    *(undefined4 *)(in_ECX + 0x18) = 0xff;
  }
  iVar3 = CFEPLanguageTest__Helper_00465a20
                    ((void *)(in_ECX + 0x1c),in_stack_00000014,in_stack_0000000c - _DAT_005d8bc0);
  *(int *)(in_ECX + 0x1f64) = iVar3;
  iVar1 = *(int *)(in_stack_00000018 + 0x54);
  *(int *)(in_ECX + 0x1f60) = iVar1;
  fVar2 = (float)iVar1 * (float)iVar3 + _DAT_005d8bc0;
  *(float *)(in_ECX + 0x10) = fVar2;
  if (*(int *)(in_ECX + 0x1f90) != 0) {
    fVar2 = fVar2 + _DAT_005db2b8;
    *(undefined4 *)(in_ECX + 0x1f98) = 0;
    *(undefined4 *)(in_ECX + 0x1f8c) = 1;
    *(float *)(in_ECX + 0x10) = fVar2;
    return *(int *)(in_ECX + 0x1f90);
  }
  if (in_stack_00000028 != 1) {
    if (in_stack_00000028 == 2) {
      pvVar4 = CPlatform__Font(&DAT_0088a0a8,0);
      pvVar5 = *(void **)(in_ECX + 0x1f98);
      *(float *)(in_ECX + 0x10) =
           (float)(*(int *)((int)pvVar4 + 0x54) * 2) + *(float *)(in_ECX + 0x10);
      if (pvVar5 == (void *)0x2) {
        *(undefined4 *)(in_ECX + 0x1fa0) = 0;
        *(undefined4 *)(in_ECX + 0x1f8c) = 1;
        return 2;
      }
      goto LAB_0044d547;
    }
    if (in_stack_00000028 + -3 != 0) {
      *(undefined4 *)(in_ECX + 0x1f8c) = 1;
      return in_stack_00000028 + -3;
    }
  }
  pvVar5 = CPlatform__Font(&DAT_0088a0a8,0);
  *(float *)(in_ECX + 0x10) = (float)*(int *)((int)pvVar5 + 0x54) + *(float *)(in_ECX + 0x10);
LAB_0044d547:
  *(undefined4 *)(in_ECX + 0x1f8c) = 1;
  return (int)pvVar5;
}
