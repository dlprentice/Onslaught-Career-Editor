/* address: 0x00424920 */
/* name: CGeneralVolume__Helper_00424920 */
/* signature: void __fastcall CGeneralVolume__Helper_00424920(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CGeneralVolume__Helper_00424920(int param_1)

{
  void *this;
  int iVar1;
  void *unaff_ESI;
  float10 fVar2;
  char *pcVar3;

  pcVar3 = s_flytowalk_006234bc;
  this = (void *)(**(code **)(**(int **)(param_1 + 0x8c) + 0x24))();
  iVar1 = FindAnimationIndex(this,(int)pcVar3,unaff_ESI);
  *(int *)(param_1 + 0x11c) = iVar1;
  if (*(int **)(param_1 + 0x8c) == (int *)0x0) {
    fVar2 = (float10)_DAT_005d856c;
  }
  else {
    fVar2 = (float10)(**(code **)(**(int **)(param_1 + 0x8c) + 0x38))(iVar1,param_1 + 0x118);
  }
  *(float *)(param_1 + 0x120) = (float)fVar2;
  *(undefined4 *)(param_1 + 0x124) = 0;
  *(undefined4 *)(param_1 + 0x128) = 0;
  *(undefined4 *)(param_1 + 0x114) = 1;
  return;
}
