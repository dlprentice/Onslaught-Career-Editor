/* address: 0x0058bd87 */
/* name: CTexture__GetNextTokenWithPreprocessor */
/* signature: uint __thiscall CTexture__GetNextTokenWithPreprocessor(void * this, int param_1, void * param_2) */


uint __thiscall CTexture__GetNextTokenWithPreprocessor(void *this,int param_1,void *param_2)

{
  void *this_00;
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  char *pcVar6;
  void *unaff_EDI;
  undefined4 *puVar7;
  char *pcVar8;
  bool bVar9;
  void *local_c;
  void *local_8;

  local_c = this;
  local_8 = this;
LAB_0058bfbc:
  do {
    if (*(int *)((int)this + 0x30) != 0) {
      uVar1 = 0x80004005;
LAB_0058bfcf:
      *(undefined4 *)(param_1 + 0x10) = *(undefined4 *)(*(int *)((int)this + 0x54) + 0x18);
      *(undefined4 *)(param_1 + 0x14) = *(undefined4 *)(*(int *)((int)this + 0x54) + 0x1c);
      *(undefined4 *)param_1 = 0xd;
      return uVar1;
    }
    if ((*(int *)((int)this + 0x48) != 0) && (*(int *)(*(int *)((int)this + 0x48) + 8) == 0)) {
      uVar1 = 0;
      goto LAB_0058bfcf;
    }
    puVar5 = *(undefined4 **)((int)this + 0x44);
    if (puVar5 == (undefined4 *)0x0) {
      uVar1 = CTexture__Unk_0058d2ad
                        (*(void **)((int)this + 0x54),*(void **)((int)this + 0x80),param_1,unaff_EDI
                        );
      if ((int)uVar1 < 0) {
        return uVar1;
      }
    }
    else {
      puVar4 = puVar5 + 4;
      puVar7 = (undefined4 *)param_1;
      for (iVar2 = 8; iVar2 != 0; iVar2 = iVar2 + -1) {
        *puVar7 = *puVar4;
        puVar4 = puVar4 + 1;
        puVar7 = puVar7 + 1;
      }
      *(undefined4 *)((int)this + 0x44) = *(undefined4 *)(*(int *)((int)this + 0x44) + 0xc);
      puVar5[3] = 0;
      (**(code **)*puVar5)(1);
      *(undefined4 *)(param_1 + 0x10) = *(undefined4 *)(*(int *)((int)this + 0x54) + 0x18);
      *(undefined4 *)(param_1 + 0x14) = *(undefined4 *)(*(int *)((int)this + 0x54) + 0x1c);
      *(undefined4 *)((int)this + 0x28) = 0;
    }
    if (*(int *)param_1 != 1) {
LAB_0058bf25:
      if (*(int *)param_1 == 0xd) {
        if (*(int *)(*(int *)((int)this + 0x50) + 0x38) != 0) {
          CTexture__Helper_0058c893((void *)((int)this + 4),param_1,0x5de,0x5ea6cc);
        }
        this_00 = *(void **)((int)this + 0x50);
        if (*(int *)((int)this_00 + 0x6c) == 0) {
          return 0;
        }
        *(undefined4 *)((int)this + 0x50) = *(undefined4 *)((int)this_00 + 0x6c);
        *(undefined4 *)((int)this_00 + 0x6c) = 0;
        CTexture__Helper_0058948d(this_00,(void *)0x1,(int)unaff_EDI);
        *(undefined4 *)((int)this + 0x54) = *(undefined4 *)((int)this + 0x50);
        *(undefined4 *)param_1 = 0xc;
        *(undefined4 *)((int)this + 0x28) = 1;
        return 0;
      }
      if (((*(int *)param_1 != 9) ||
          (iVar2 = CTexture__Helper_0058a60a(*(void **)(param_1 + 8),&local_c,&local_8), iVar2 == 0)
          ) || (iVar2 = CTexture__Helper_0058aacf(), iVar2 == 0)) {
        if (*(int *)param_1 == 9) {
          iVar2 = 9;
          bVar9 = true;
          pcVar6 = *(char **)(param_1 + 8);
          pcVar8 = "__FILE__";
          do {
            if (iVar2 == 0) break;
            iVar2 = iVar2 + -1;
            bVar9 = *pcVar6 == *pcVar8;
            pcVar6 = pcVar6 + 1;
            pcVar8 = pcVar8 + 1;
          } while (bVar9);
          if (bVar9) {
            *(undefined4 *)param_1 = 10;
            uVar3 = *(undefined4 *)(*(int *)((int)this + 0x54) + 0x18);
          }
          else {
            iVar2 = 9;
            bVar9 = true;
            pcVar6 = *(char **)(param_1 + 8);
            pcVar8 = "__LINE__";
            do {
              if (iVar2 == 0) break;
              iVar2 = iVar2 + -1;
              bVar9 = *pcVar6 == *pcVar8;
              pcVar6 = pcVar6 + 1;
              pcVar8 = pcVar8 + 1;
            } while (bVar9);
            if (!bVar9) goto LAB_0058bfa6;
            *(undefined4 *)param_1 = 2;
            uVar3 = *(undefined4 *)(*(int *)((int)this + 0x54) + 0x1c);
          }
          *(undefined4 *)(param_1 + 8) = uVar3;
        }
LAB_0058bfa6:
        *(uint *)((int)this + 0x28) = (uint)(*(int *)param_1 == 0xc);
        if (*(int *)((int)this + 0x38) != 0) {
          iVar2 = *(int *)((int)this + 0x48);
          if ((iVar2 != 0) && (*(int *)(iVar2 + 4) != 0)) {
            if ((*(int *)param_1 == 1) && (*(char *)(param_1 + 9) == '\0')) {
              if (*(char *)(param_1 + 8) == '{') {
                *(int *)(iVar2 + 8) = *(int *)(iVar2 + 8) + 1;
              }
              if (*(char *)(param_1 + 8) == '}') {
                iVar2 = *(int *)(*(int *)((int)this + 0x48) + 8);
                if (iVar2 != 0) {
                  *(int *)(*(int *)((int)this + 0x48) + 8) = iVar2 + -1;
                }
              }
            }
            if (*(int *)(*(int *)((int)this + 0x48) + 8) == 0) {
              *(undefined4 *)param_1 = 0xd;
            }
          }
          return 0;
        }
      }
      goto LAB_0058bfbc;
    }
    iVar2 = 2;
    bVar9 = true;
    pcVar6 = "#";
    pcVar8 = (char *)(param_1 + 8);
    do {
      if (iVar2 == 0) break;
      iVar2 = iVar2 + -1;
      bVar9 = *pcVar6 == *pcVar8;
      pcVar6 = pcVar6 + 1;
      pcVar8 = pcVar8 + 1;
    } while (bVar9);
    if ((!bVar9) || (*(int *)((int)this + 0x28) == 0)) goto LAB_0058bf25;
    DAT_009d1838 = this;
    *(undefined4 *)((int)this + 0x28) = 0;
    *(undefined4 *)((int)this + 0x2c) = 0;
    *(undefined4 *)((int)this + 0x34) = 1;
    *(undefined4 *)((int)this + 0x3c) = *(undefined4 *)((int)this + 0x38);
    iVar2 = CTexture__RunDirectiveParser();
    if (iVar2 != 0) {
      *(undefined4 *)((int)this + 0x2c) = 1;
    }
    if (*(undefined4 **)((int)this + 0x40) != (undefined4 *)0x0) {
      (**(code **)**(undefined4 **)((int)this + 0x40))(1);
    }
    *(undefined4 *)((int)this + 0x40) = 0;
    if ((*(int *)((int)this + 0x28) == 0) && (*(int *)((int)this + 0x2c) == 0)) {
      uVar1 = CTexture__Unk_0058d2ad
                        (*(void **)((int)this + 0x54),*(void **)((int)this + 0x80),(int)this + 0x60,
                         unaff_EDI);
      if ((int)uVar1 < 0) {
        return uVar1;
      }
      iVar2 = *(int *)((int)this + 0x60);
      if ((iVar2 == 0xc) || (iVar2 == 0xd)) {
        *(undefined4 *)((int)this + 0x28) = 1;
      }
      else {
        if (*(int *)((int)this + 0x38) != 0) {
          CTexture__Helper_0058c893((void *)((int)this + 4),param_1,0x5dd,0x5ea6fc);
        }
        *(undefined4 *)((int)this + 0x2c) = 1;
      }
    }
    if (*(int *)((int)this + 0x28) == 0) {
      CTexture__Unk_0058c3fe(*(void **)((int)this + 0x54));
      if (*(undefined4 **)((int)this + 0x44) != (undefined4 *)0x0) {
        (**(code **)**(undefined4 **)((int)this + 0x44))(1);
      }
      *(undefined4 *)((int)this + 0x44) = 0;
      uVar1 = CTexture__Unk_0058d2ad
                        (*(void **)((int)this + 0x54),*(void **)((int)this + 0x80),(int)this + 0x60,
                         unaff_EDI);
      if ((int)uVar1 < 0) {
        return uVar1;
      }
      *(undefined4 *)((int)this + 0x28) = 1;
    }
    *(undefined4 *)((int)this + 0x54) = *(undefined4 *)((int)this + 0x50);
    *(int *)((int)this + 0x38) = *(int *)((int)this + 0x3c);
    if (*(int *)((int)this + 0x3c) != 0) {
      puVar5 = (undefined4 *)((int)this + 0x60);
      for (iVar2 = 8; iVar2 != 0; iVar2 = iVar2 + -1) {
        *(undefined4 *)param_1 = *puVar5;
        puVar5 = puVar5 + 1;
        param_1 = (int)(param_1 + 4);
      }
      return -(uint)(*(int *)((int)this + 0x30) != 0) & 0x80004005;
    }
  } while( true );
}
