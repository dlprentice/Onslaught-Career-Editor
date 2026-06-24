/* address: 0x0058d2ad */
/* name: CTexture__ReadNextLexToken */
/* signature: int __thiscall CTexture__ReadNextLexToken(void * this, void * param_1, int param_2, void * param_3) */


int __thiscall CTexture__ReadNextLexToken(void *this,void *param_1,int param_2,void *param_3)

{
  int iVar1;
  int iVar2;
  char *pcVar3;
  void *unaff_EDI;

  *(void **)((int)this + 0x28) = param_1;
  *(undefined4 *)(param_2 + 0x10) = *(undefined4 *)((int)this + 0x18);
  pcVar3 = (char *)0x0;
  *(undefined4 *)(param_2 + 0x14) = *(undefined4 *)((int)this + 0x1c);
  iVar1 = CTexture__Helper_0058cc00(this);
  if (iVar1 == 0) {
    *(undefined4 *)(param_2 + 0x10) = *(undefined4 *)((int)this + 0x18);
    *(undefined4 *)(param_2 + 0x14) = *(undefined4 *)((int)this + 0x1c);
    if (*(void **)this < *(void **)((int)this + 4)) {
      iVar1 = CTexture__Unk_0058c457(this,*(void **)this,(void *)(param_2 + 8),unaff_EDI);
      if (iVar1 == 0) {
        pcVar3 = CTexture__Unk_0058d18b(this,*(void **)this,(void *)(param_2 + 8),unaff_EDI);
        if (pcVar3 != (char *)0x0) {
          *(undefined4 *)param_2 = 2;
          goto LAB_0058d407;
        }
        iVar1 = CTexture__Helper_0058cd30(this,*(void **)this,(void *)(param_2 + 8),unaff_EDI);
        if (iVar1 == 0) {
          iVar1 = CTexture__Helper_0058cdd5(this,*(int *)this,(void *)(param_2 + 8),unaff_EDI);
          if (iVar1 == 0) {
            iVar1 = CTexture__Helper_0058ce51(this,*(void **)this,(void *)(param_2 + 8),unaff_EDI);
            if (iVar1 == 0) {
              pcVar3 = CTexture__Unk_0058d1ca(this,*(void **)this,(void *)(param_2 + 8),unaff_EDI);
              if (pcVar3 == (char *)0x0) {
                pcVar3 = CTexture__Helper_0058d088
                                   (this,*(void **)this,(void *)(param_2 + 8),unaff_EDI);
                if (pcVar3 == (char *)0x0) {
                  pcVar3 = (char *)CTexture__Unk_0058c5d3
                                             (this,*(void **)this,(void *)(param_2 + 8),unaff_EDI);
                  if (pcVar3 == (char *)0x0) {
                    pcVar3 = (char *)CTexture__Unk_0058c652
                                               (this,*(int *)this,(void *)(param_2 + 8),unaff_EDI);
                    *(undefined4 *)param_2 = 1;
                  }
                  else {
                    *(undefined4 *)param_2 = 9;
                  }
                }
                else {
                  *(undefined4 *)param_2 = 0;
                }
              }
              else {
                *(uint *)param_2 = (**(char **)this != '\"') + 10;
              }
              goto LAB_0058d407;
            }
          }
        }
        *(undefined4 *)param_2 = 2;
        iVar2 = CTexture__Helper_0058c7a4(this,*(int *)this + iVar1,(void *)param_2,unaff_EDI);
      }
      else {
        *(undefined4 *)param_2 = 5;
        iVar2 = CTexture__Helper_0058c75e(this,*(int *)this + iVar1,(void *)param_2,unaff_EDI);
      }
      pcVar3 = (char *)(iVar1 + iVar2);
    }
    else {
      *(undefined4 *)param_2 = 0xd;
    }
  }
  else {
    *(undefined4 *)param_2 = 0xc;
  }
LAB_0058d407:
  *(undefined4 *)(param_2 + 0x18) = *(undefined4 *)this;
  *(char **)(param_2 + 0x1c) = pcVar3;
  *(char **)this = pcVar3 + *(int *)this;
  return 0;
}
