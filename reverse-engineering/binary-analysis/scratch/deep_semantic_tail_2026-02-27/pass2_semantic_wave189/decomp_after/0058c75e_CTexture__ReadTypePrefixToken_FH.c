/* address: 0x0058c75e */
/* name: CTexture__ReadTypePrefixToken_FH */
/* signature: int __thiscall CTexture__ReadTypePrefixToken_FH(void * this, int param_1, void * param_2, void * param_3) */


int __thiscall CTexture__ReadTypePrefixToken_FH(void *this,int param_1,void *param_2,void *param_3)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;

  uVar3 = 5;
  if (*(uint *)((int)this + 4) <= (uint)param_1) {
    return 0;
  }
  iVar1 = CRT__ToLower_005695af((int)*(char *)param_1);
  if (iVar1 == 0x66) {
    uVar3 = 7;
  }
  else {
    iVar2 = param_1;
    if (iVar1 != 0x68) goto LAB_0058c790;
    uVar3 = 6;
  }
  iVar2 = param_1 + 1;
LAB_0058c790:
  if (param_2 != (void *)0x0) {
    *(undefined4 *)param_2 = uVar3;
  }
  return iVar2 - param_1;
}
