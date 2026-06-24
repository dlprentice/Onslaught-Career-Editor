/* address: 0x0058c08a */
/* name: CTexture__Helper_0058c08a */
/* signature: int __fastcall CTexture__Helper_0058c08a(int param_1) */


int __fastcall CTexture__Helper_0058c08a(int param_1)

{
  void *this;
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  void *unaff_ESI;
  int local_24 [8];

  if (*(int *)(param_1 + 0x48) == 0) {
    iVar1 = -0x7789f794;
  }
  else {
    do {
      uVar2 = CTexture__GetNextTokenWithPreprocessor((void *)param_1,(int)local_24,unaff_ESI);
      if ((int)uVar2 < 0) {
        return uVar2;
      }
    } while (local_24[0] != 0xd);
    this = *(void **)(param_1 + 0x48);
    *(undefined4 *)(param_1 + 0x48) = *(undefined4 *)((int)this + 4);
    *(undefined4 *)((int)this + 4) = 0;
    CTexture__Helper_005896a1(this,(void *)0x1,(int)unaff_ESI);
    if (*(undefined4 **)(param_1 + 0x48) == (undefined4 *)0x0) {
      uVar3 = 1;
    }
    else {
      uVar3 = **(undefined4 **)(param_1 + 0x48);
    }
    *(undefined4 *)(param_1 + 0x80) = uVar3;
    iVar1 = 0;
  }
  return iVar1;
}
