/* address: 0x00568c4e */
/* name: CDXTexture__Unk_00568c4e */
/* signature: int __cdecl CDXTexture__Unk_00568c4e(int param_1, void * param_2) */


int __cdecl CDXTexture__Unk_00568c4e(int param_1,void *param_2)

{
  code *pcVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  int iVar7;

  iVar4 = CTexture__Helper_00560b93();
  piVar5 = CDXTexture__Helper_00568d8c(param_1,*(void **)(iVar4 + 0x50));
  if ((piVar5 == (int *)0x0) || (pcVar1 = (code *)piVar5[2], pcVar1 == (code *)0x0)) {
    iVar4 = UnhandledExceptionFilter(param_2);
  }
  else if (pcVar1 == (code *)0x5) {
    piVar5[2] = 0;
    iVar4 = 1;
  }
  else {
    if (pcVar1 != (code *)0x1) {
      uVar2 = *(undefined4 *)(iVar4 + 0x54);
      *(void **)(iVar4 + 0x54) = param_2;
      if (piVar5[1] == 8) {
        if (DAT_00656120 < DAT_00656124 + DAT_00656120) {
          iVar6 = DAT_00656120 * 0xc;
          iVar7 = DAT_00656120;
          do {
            *(undefined4 *)(iVar6 + 8 + *(int *)(iVar4 + 0x50)) = 0;
            iVar7 = iVar7 + 1;
            iVar6 = iVar6 + 0xc;
          } while (iVar7 < DAT_00656124 + DAT_00656120);
        }
        iVar6 = *piVar5;
        uVar3 = *(undefined4 *)(iVar4 + 0x58);
        if (iVar6 == -0x3fffff72) {
          *(undefined4 *)(iVar4 + 0x58) = 0x83;
        }
        else if (iVar6 == -0x3fffff70) {
          *(undefined4 *)(iVar4 + 0x58) = 0x81;
        }
        else if (iVar6 == -0x3fffff6f) {
          *(undefined4 *)(iVar4 + 0x58) = 0x84;
        }
        else if (iVar6 == -0x3fffff6d) {
          *(undefined4 *)(iVar4 + 0x58) = 0x85;
        }
        else if (iVar6 == -0x3fffff73) {
          *(undefined4 *)(iVar4 + 0x58) = 0x82;
        }
        else if (iVar6 == -0x3fffff71) {
          *(undefined4 *)(iVar4 + 0x58) = 0x86;
        }
        else if (iVar6 == -0x3fffff6e) {
          *(undefined4 *)(iVar4 + 0x58) = 0x8a;
        }
        (*pcVar1)(8,*(undefined4 *)(iVar4 + 0x58));
        *(undefined4 *)(iVar4 + 0x58) = uVar3;
      }
      else {
        piVar5[2] = 0;
        (*pcVar1)(piVar5[1]);
      }
      *(undefined4 *)(iVar4 + 0x54) = uVar2;
    }
    iVar4 = -1;
  }
  return iVar4;
}
