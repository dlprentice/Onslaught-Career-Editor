/* address: 0x0058a1e3 */
/* name: CTexture__HandlePragma_Warning */
/* signature: int __fastcall CTexture__HandlePragma_Warning(int param_1) */


int __fastcall CTexture__HandlePragma_Warning(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 *extraout_EAX;
  undefined4 *extraout_EAX_00;
  int extraout_EAX_01;
  int iVar3;
  uint uVar4;
  char *pcVar5;
  undefined4 *puVar6;
  char *pcVar7;
  void *unaff_EDI;
  char *pcVar8;
  undefined4 *puVar9;
  bool bVar10;
  uint local_18;
  uint local_14;
  undefined4 *local_10;
  undefined4 *local_c;
  uint local_8;

  local_c = (undefined4 *)0x0;
  local_10 = (undefined4 *)0x0;
  iVar2 = CTexture__ReadNextLexToken
                    (*(void **)(param_1 + 0x54),*(void **)(param_1 + 0x80),param_1 + 0x60,unaff_EDI)
  ;
  if (iVar2 < 0) goto LAB_0058a4e2;
  if (*(int *)(param_1 + 0x60) == 1) {
    iVar2 = 2;
    bVar10 = true;
    pcVar7 = (char *)(param_1 + 0x68);
    pcVar5 = "(";
    do {
      if (iVar2 == 0) break;
      iVar2 = iVar2 + -1;
      bVar10 = *pcVar7 == *pcVar5;
      pcVar7 = pcVar7 + 1;
      pcVar5 = pcVar5 + 1;
    } while (bVar10);
    if (bVar10) {
      iVar2 = CTexture__ReadNextLexToken
                        (*(void **)(param_1 + 0x54),*(void **)(param_1 + 0x80),param_1 + 0x60,
                         unaff_EDI);
      if (iVar2 < 0) goto LAB_0058a4e2;
      local_8 = 0;
      do {
        do {
          do {
            iVar2 = *(int *)(param_1 + 0x60);
            if (iVar2 == 1) {
              iVar3 = 2;
              bVar10 = true;
              pcVar7 = (char *)(param_1 + 0x68);
              pcVar5 = ")";
              do {
                if (iVar3 == 0) break;
                iVar3 = iVar3 + -1;
                bVar10 = *pcVar7 == *pcVar5;
                pcVar7 = pcVar7 + 1;
                pcVar5 = pcVar5 + 1;
              } while (bVar10);
              if (bVar10) {
                iVar2 = CTexture__ReadNextLexToken
                                  (*(void **)(param_1 + 0x54),*(void **)(param_1 + 0x80),
                                   param_1 + 0x60,unaff_EDI);
                if (iVar2 < 0) goto LAB_0058a4e2;
                iVar2 = *(int *)(param_1 + 0x60);
                if ((iVar2 == 0xc) || (iVar2 == 0xd)) {
                  local_18 = 0;
                  if (local_8 == 0) goto LAB_0058a4e0;
                  puVar6 = local_10;
                  goto LAB_0058a548;
                }
                goto LAB_0058a4cb;
              }
            }
            if (iVar2 == 9) {
              pcVar7 = *(char **)(param_1 + 0x68);
              iVar2 = 5;
              bVar10 = true;
              pcVar5 = pcVar7;
              pcVar8 = "once";
              do {
                if (iVar2 == 0) break;
                iVar2 = iVar2 + -1;
                bVar10 = *pcVar5 == *pcVar8;
                pcVar5 = pcVar5 + 1;
                pcVar8 = pcVar8 + 1;
              } while (bVar10);
              if (bVar10) {
                local_14 = 0x10;
              }
              else {
                iVar2 = 6;
                bVar10 = true;
                pcVar5 = pcVar7;
                pcVar8 = "error";
                do {
                  if (iVar2 == 0) break;
                  iVar2 = iVar2 + -1;
                  bVar10 = *pcVar5 == *pcVar8;
                  pcVar5 = pcVar5 + 1;
                  pcVar8 = pcVar8 + 1;
                } while (bVar10);
                if (bVar10) {
                  local_14 = 0xf;
                }
                else {
                  iVar2 = 8;
                  bVar10 = true;
                  pcVar5 = pcVar7;
                  pcVar8 = "disable";
                  do {
                    if (iVar2 == 0) break;
                    iVar2 = iVar2 + -1;
                    bVar10 = *pcVar5 == *pcVar8;
                    pcVar5 = pcVar5 + 1;
                    pcVar8 = pcVar8 + 1;
                  } while (bVar10);
                  if (bVar10) {
                    local_14 = 0;
                  }
                  else {
                    iVar2 = 8;
                    bVar10 = true;
                    pcVar5 = "default";
                    do {
                      if (iVar2 == 0) break;
                      iVar2 = iVar2 + -1;
                      bVar10 = *pcVar7 == *pcVar5;
                      pcVar7 = pcVar7 + 1;
                      pcVar5 = pcVar5 + 1;
                    } while (bVar10);
                    if (!bVar10) goto LAB_0058a4cb;
                    local_14 = 0xff;
                  }
                }
              }
            }
            else if ((((iVar2 != 2) && (iVar2 != 3)) && (iVar2 != 4)) ||
                    ((local_14 = *(uint *)(param_1 + 0x68), local_14 == 0 || (4 < local_14))))
            goto LAB_0058a4cb;
            iVar2 = CTexture__ReadNextLexToken
                              (*(void **)(param_1 + 0x54),*(void **)(param_1 + 0x80),param_1 + 0x60,
                               unaff_EDI);
            if (iVar2 < 0) goto LAB_0058a4e2;
            if (*(int *)(param_1 + 0x60) != 1) goto LAB_0058a4cb;
            iVar2 = 2;
            bVar10 = true;
            pcVar7 = (char *)(param_1 + 0x68);
            pcVar5 = ":";
            do {
              if (iVar2 == 0) break;
              iVar2 = iVar2 + -1;
              bVar10 = *pcVar7 == *pcVar5;
              pcVar7 = pcVar7 + 1;
              pcVar5 = pcVar5 + 1;
            } while (bVar10);
            if (!bVar10) goto LAB_0058a4cb;
            iVar2 = CTexture__ReadNextLexToken
                              (*(void **)(param_1 + 0x54),*(void **)(param_1 + 0x80),param_1 + 0x60,
                               unaff_EDI);
            if (iVar2 < 0) goto LAB_0058a4e2;
            do {
              do {
                iVar2 = *(int *)(param_1 + 0x60);
                if (((iVar2 != 2) && (iVar2 != 3)) && (iVar2 != 4)) goto LAB_0058a4cb;
                uVar1 = *(undefined4 *)(param_1 + 0x68);
                if (local_8 == (~local_8 + 1 & local_8)) {
                  if (local_8 == 0) {
                    iVar2 = 1;
                  }
                  else {
                    iVar2 = local_8 * 2;
                  }
                  OID__AllocObject_DefaultTag_00662b2c(iVar2 << 2);
                  if (extraout_EAX != (undefined4 *)0x0) {
                    puVar6 = local_c;
                    puVar9 = extraout_EAX;
                    for (uVar4 = local_8 & 0x3fffffff; uVar4 != 0; uVar4 = uVar4 - 1) {
                      *puVar9 = *puVar6;
                      puVar6 = puVar6 + 1;
                      puVar9 = puVar9 + 1;
                    }
                    for (iVar2 = 0; iVar2 != 0; iVar2 = iVar2 + -1) {
                      *(undefined1 *)puVar9 = *(undefined1 *)puVar6;
                      puVar6 = (undefined4 *)((int)puVar6 + 1);
                      puVar9 = (undefined4 *)((int)puVar9 + 1);
                    }
                    OID__FreeObject_Callback(local_c);
                    if (local_8 == 0) {
                      iVar2 = 1;
                    }
                    else {
                      iVar2 = local_8 * 2;
                    }
                    OID__AllocObject_DefaultTag_00662b2c(iVar2 << 2);
                    local_c = extraout_EAX;
                    if (extraout_EAX_00 != (undefined4 *)0x0) {
                      puVar6 = local_10;
                      puVar9 = extraout_EAX_00;
                      for (uVar4 = local_8 & 0x3fffffff; uVar4 != 0; uVar4 = uVar4 - 1) {
                        *puVar9 = *puVar6;
                        puVar6 = puVar6 + 1;
                        puVar9 = puVar9 + 1;
                      }
                      for (iVar2 = 0; iVar2 != 0; iVar2 = iVar2 + -1) {
                        *(undefined1 *)puVar9 = *(undefined1 *)puVar6;
                        puVar6 = (undefined4 *)((int)puVar6 + 1);
                        puVar9 = (undefined4 *)((int)puVar9 + 1);
                      }
                      OID__FreeObject_Callback(local_10);
                      local_10 = extraout_EAX_00;
                      goto LAB_0058a41e;
                    }
                  }
                  iVar2 = -0x7ff8fff2;
                  goto LAB_0058a4e2;
                }
LAB_0058a41e:
                local_10[local_8] = uVar1;
                local_c[local_8] = local_14;
                local_8 = local_8 + 1;
                iVar2 = CTexture__ReadNextLexToken
                                  (*(void **)(param_1 + 0x54),*(void **)(param_1 + 0x80),
                                   param_1 + 0x60,unaff_EDI);
                if (iVar2 < 0) goto LAB_0058a4e2;
              } while (*(int *)(param_1 + 0x60) != 1);
              iVar2 = 2;
              bVar10 = true;
              pcVar7 = (char *)(param_1 + 0x68);
              pcVar5 = ";";
              do {
                if (iVar2 == 0) break;
                iVar2 = iVar2 + -1;
                bVar10 = *pcVar7 == *pcVar5;
                pcVar7 = pcVar7 + 1;
                pcVar5 = pcVar5 + 1;
              } while (bVar10);
              if (bVar10) break;
              iVar2 = 2;
              bVar10 = true;
              pcVar7 = (char *)(param_1 + 0x68);
              pcVar5 = ")";
              do {
                if (iVar2 == 0) break;
                iVar2 = iVar2 + -1;
                bVar10 = *pcVar7 == *pcVar5;
                pcVar7 = pcVar7 + 1;
                pcVar5 = pcVar5 + 1;
              } while (bVar10);
            } while (!bVar10);
            iVar2 = 2;
            bVar10 = true;
            pcVar7 = (char *)(param_1 + 0x68);
            pcVar5 = ";";
            do {
              if (iVar2 == 0) break;
              iVar2 = iVar2 + -1;
              bVar10 = *pcVar7 == *pcVar5;
              pcVar7 = pcVar7 + 1;
              pcVar5 = pcVar5 + 1;
            } while (bVar10);
          } while (!bVar10);
          iVar2 = CTexture__ReadNextLexToken
                            (*(void **)(param_1 + 0x54),*(void **)(param_1 + 0x80),param_1 + 0x60,
                             unaff_EDI);
          if (iVar2 < 0) goto LAB_0058a4e2;
        } while (*(int *)(param_1 + 0x60) != 1);
        iVar2 = 2;
        bVar10 = true;
        pcVar7 = (char *)(param_1 + 0x68);
        pcVar5 = ")";
        do {
          if (iVar2 == 0) break;
          iVar2 = iVar2 + -1;
          bVar10 = *pcVar7 == *pcVar5;
          pcVar7 = pcVar7 + 1;
          pcVar5 = pcVar5 + 1;
        } while (bVar10);
      } while (!bVar10);
    }
  }
LAB_0058a4cb:
  if ((*(int *)(param_1 + 0x60) != 0xc) && (*(int *)(param_1 + 0x60) != 0xd)) {
    CTexture__SkipLineContinuationAndAdvance(*(void **)(param_1 + 0x54));
  }
  goto LAB_0058a4e0;
  while( true ) {
    local_18 = local_18 + 1;
    puVar6 = puVar6 + 1;
    if (local_8 <= local_18) break;
LAB_0058a548:
    CDXTexture__SetKeyEntryModeFlags
              ((void *)(param_1 + 4),(void *)*puVar6,
               *(int *)(((int)local_c - (int)local_10) + (int)puVar6),(uint)unaff_EDI);
    iVar2 = extraout_EAX_01;
    if (extraout_EAX_01 < 0) goto LAB_0058a4e2;
  }
LAB_0058a4e0:
  iVar2 = 0;
LAB_0058a4e2:
  OID__FreeObject_Callback(local_c);
  OID__FreeObject_Callback(local_10);
  OID__FreeObject_Callback((void *)0x0);
  *(undefined4 *)(param_1 + 0x28) = 1;
  return iVar2;
}
