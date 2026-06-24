/* address: 0x0059aec0 */
/* name: CTexture__Helper_0059aec0 */
/* signature: int __fastcall CTexture__Helper_0059aec0(int param_1, int param_2) */


int __fastcall CTexture__Helper_0059aec0(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;

  if (((((*(int *)(param_2 + 0x4c) != 0) || (*(int *)(param_2 + 0x130) != 0)) ||
       (*(int *)(param_2 + 0x28) != 3)) ||
      (((*(int *)(param_2 + 0x24) != 3 || (*(int *)(param_2 + 0x2c) != 2)) ||
       ((*(int *)(param_2 + 0x78) != 3 ||
        ((iVar1 = *(int *)(param_2 + 0xdc), *(int *)(iVar1 + 8) != 2 ||
         (iVar3 = 1, *(int *)(iVar1 + 0x5c) != 1)))))))) ||
     ((*(int *)(iVar1 + 0xb0) != 1 ||
      (((((2 < *(int *)(iVar1 + 0xc) || (*(int *)(iVar1 + 0x60) != 1)) ||
         (*(int *)(iVar1 + 0xb4) != 1)) ||
        ((iVar2 = *(int *)(param_2 + 0x140), *(int *)(iVar1 + 0x24) != iVar2 ||
         (*(int *)(iVar1 + 0x78) != iVar2)))) || (*(int *)(iVar1 + 0xcc) != iVar2)))))) {
    iVar3 = 0;
  }
  return iVar3;
}
