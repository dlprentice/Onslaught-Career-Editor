/* address: 0x005740a0 */
/* name: CTexture__Unk_005740a0 */
/* signature: void __thiscall CTexture__Unk_005740a0(void * this, int param_1, void * param_2) */


void __thiscall CTexture__Unk_005740a0(void *this,int param_1,void *param_2)

{
  int iVar1;
  int *piVar2;

  iVar1 = *(int *)param_1;
  *(undefined4 *)param_1 = *(undefined4 *)(iVar1 + 8);
  if (*(int *)(iVar1 + 8) != DAT_009d0c44) {
    *(int *)(*(int *)(iVar1 + 8) + 4) = param_1;
  }
  *(undefined4 *)(iVar1 + 4) = *(undefined4 *)(param_1 + 4);
  if (param_1 == *(int *)(*(int *)((int)this + 4) + 4)) {
    *(int *)(*(int *)((int)this + 4) + 4) = iVar1;
    *(int *)(iVar1 + 8) = param_1;
    *(int *)(param_1 + 4) = iVar1;
    return;
  }
  piVar2 = *(int **)(param_1 + 4);
  if (param_1 == piVar2[2]) {
    piVar2[2] = iVar1;
    *(int *)(iVar1 + 8) = param_1;
    *(int *)(param_1 + 4) = iVar1;
    return;
  }
  *piVar2 = iVar1;
  *(int *)(iVar1 + 8) = param_1;
  *(int *)(param_1 + 4) = iVar1;
  return;
}
