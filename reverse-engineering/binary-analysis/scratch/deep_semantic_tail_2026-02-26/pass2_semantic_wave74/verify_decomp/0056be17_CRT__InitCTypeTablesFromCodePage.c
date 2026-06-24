/* address: 0x0056be17 */
/* name: CRT__InitCTypeTablesFromCodePage */
/* signature: int CRT__InitCTypeTablesFromCodePage(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CRT__InitCTypeTablesFromCodePage(void)

{
  BYTE *pBVar1;
  byte bVar2;
  int iVar3;
  undefined2 *puVar4;
  BOOL BVar5;
  BYTE *pBVar6;
  uint uVar7;
  undefined2 *puVar8;
  int iVar9;
  _cpinfo local_28;
  undefined2 *local_14;
  undefined2 *local_10;
  undefined2 *local_c;
  void *local_8;

  iVar9 = 0;
  local_8 = (void *)0x0;
  local_c = (undefined2 *)0x0;
  if (DAT_009d0998 == 0) {
    PTR_DAT_00653890 = &DAT_0065389a;
    PTR_DAT_00653894 = &DAT_0065389a;
    CMeshCollisionVolume__Unk_0055f085((int)DAT_009d0aec);
    CMeshCollisionVolume__Unk_0055f085((int)DAT_009d0af0);
    DAT_009d0aec = (undefined2 *)0x0;
    DAT_009d0af0 = (undefined2 *)0x0;
    return 0;
  }
  if ((DAT_009d09a8 != 0) ||
     (iVar3 = CTexture__Helper_0056ddc2(0,(uint)DAT_009d0b00,0x1004,&DAT_009d09a8), iVar3 == 0)) {
    puVar4 = _malloc(0x202);
    local_14 = puVar4;
    local_10 = _malloc(0x202);
    local_8 = _malloc(0x101);
    local_c = _malloc(0x202);
    if ((puVar4 != (undefined2 *)0x0) &&
       (((local_10 != (undefined2 *)0x0 && (local_8 != (void *)0x0)) &&
        (local_c != (undefined2 *)0x0)))) {
      iVar3 = 0;
      do {
        *(char *)(iVar3 + (int)local_8) = (char)iVar3;
        iVar3 = iVar3 + 1;
      } while (iVar3 < 0x100);
      BVar5 = GetCPInfo(DAT_009d09a8,&local_28);
      if ((BVar5 != 0) && (local_28.MaxCharSize < 3)) {
        DAT_00653a9c = local_28.MaxCharSize & 0xffff;
        if ((1 < DAT_00653a9c) && (local_28.LeadByte[0] != '\0')) {
          pBVar6 = local_28.LeadByte + 1;
          do {
            bVar2 = *pBVar6;
            if (bVar2 == 0) break;
            for (uVar7 = (uint)pBVar6[-1]; (int)uVar7 <= (int)(uint)bVar2; uVar7 = uVar7 + 1) {
              *(undefined1 *)(uVar7 + (int)local_8) = 0;
              bVar2 = *pBVar6;
            }
            pBVar1 = pBVar6 + 1;
            pBVar6 = pBVar6 + 2;
          } while (*pBVar1 != 0);
        }
        iVar3 = CRT__GetStringTypeACompat();
        if (iVar3 != 0) {
          *puVar4 = 0;
          iVar3 = 0;
          puVar4 = local_c;
          do {
            *puVar4 = (short)iVar3;
            puVar4 = puVar4 + 1;
            iVar3 = iVar3 + 1;
          } while (iVar3 < 0x100);
          puVar4 = local_10 + 1;
          iVar3 = CTexture__Helper_0056defa();
          if (iVar3 != 0) {
            *local_10 = 0;
            if ((1 < (int)DAT_00653a9c) && (local_28.LeadByte[0] != '\0')) {
              pBVar6 = local_28.LeadByte + 1;
              do {
                if (*pBVar6 == 0) break;
                uVar7 = (uint)pBVar6[-1];
                if (uVar7 <= *pBVar6) {
                  puVar8 = local_14 + uVar7 + 1;
                  do {
                    *puVar8 = 0x8000;
                    uVar7 = uVar7 + 1;
                    puVar8 = puVar8 + 1;
                  } while ((int)uVar7 <= (int)(uint)*pBVar6);
                }
                pBVar1 = pBVar6 + 1;
                pBVar6 = pBVar6 + 2;
              } while (*pBVar1 != 0);
            }
            PTR_DAT_00653890 = (undefined *)(local_14 + 1);
            PTR_DAT_00653894 = (undefined *)puVar4;
            if (DAT_009d0aec != (undefined2 *)0x0) {
              CMeshCollisionVolume__Unk_0055f085((int)DAT_009d0aec);
            }
            DAT_009d0aec = local_14;
            if (DAT_009d0af0 != (undefined2 *)0x0) {
              CMeshCollisionVolume__Unk_0055f085((int)DAT_009d0af0);
            }
            DAT_009d0af0 = local_10;
            goto LAB_0056bff5;
          }
        }
      }
    }
  }
  CMeshCollisionVolume__Unk_0055f085((int)local_14);
  CMeshCollisionVolume__Unk_0055f085((int)local_10);
  iVar9 = 1;
LAB_0056bff5:
  CMeshCollisionVolume__Unk_0055f085((int)local_8);
  CMeshCollisionVolume__Unk_0055f085((int)local_c);
  return iVar9;
}
