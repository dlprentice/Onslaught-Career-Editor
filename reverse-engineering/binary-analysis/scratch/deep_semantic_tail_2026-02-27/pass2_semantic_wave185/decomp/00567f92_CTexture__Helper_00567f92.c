/* address: 0x00567f92 */
/* name: CTexture__Helper_00567f92 */
/* signature: int __cdecl CTexture__Helper_00567f92(int param_1) */


int __cdecl CTexture__Helper_00567f92(int param_1)

{
  BYTE *pBVar1;
  byte *pbVar2;
  byte bVar3;
  byte bVar4;
  UINT CodePage;
  UINT *pUVar5;
  BOOL BVar6;
  uint uVar7;
  uint uVar8;
  BYTE *pBVar9;
  int iVar10;
  byte *pbVar11;
  byte *pbVar12;
  int iVar13;
  undefined4 *puVar14;
  _cpinfo local_1c;
  uint local_8;

  CRT__LockByIndex(0x19);
  CodePage = CTexture__Helper_0056813f(param_1);
  if (CodePage != DAT_009d33a4) {
    if (CodePage != 0) {
      iVar13 = 0;
      pUVar5 = &DAT_00655f28;
LAB_00567fcf:
      if (*pUVar5 != CodePage) goto code_r0x00567fd3;
      local_8 = 0;
      puVar14 = &DAT_009d34c0;
      for (iVar10 = 0x40; iVar10 != 0; iVar10 = iVar10 + -1) {
        *puVar14 = 0;
        puVar14 = puVar14 + 1;
      }
      iVar13 = iVar13 * 0x30;
      *(undefined1 *)puVar14 = 0;
      pbVar12 = (byte *)(iVar13 + 0x655f38);
      do {
        bVar3 = *pbVar12;
        pbVar11 = pbVar12;
        while ((bVar3 != 0 && (bVar3 = pbVar11[1], bVar3 != 0))) {
          uVar8 = (uint)*pbVar11;
          if (uVar8 <= bVar3) {
            bVar4 = (&DAT_00655f20)[local_8];
            do {
              pbVar2 = (byte *)((int)&DAT_009d34c0 + uVar8 + 1);
              *pbVar2 = *pbVar2 | bVar4;
              uVar8 = uVar8 + 1;
            } while (uVar8 <= bVar3);
          }
          pbVar11 = pbVar11 + 2;
          bVar3 = *pbVar11;
        }
        local_8 = local_8 + 1;
        pbVar12 = pbVar12 + 8;
      } while (local_8 < 4);
      DAT_009d33bc = 1;
      DAT_009d33a4 = CodePage;
      DAT_009d35c4 = CTexture__Helper_00568189(CodePage);
      DAT_009d33b0 = *(undefined4 *)(iVar13 + 0x655f2c);
      DAT_009d33b4 = *(undefined4 *)(iVar13 + 0x655f30);
      DAT_009d33b8 = *(undefined4 *)(iVar13 + 0x655f34);
      goto LAB_00568123;
    }
    goto LAB_0056811e;
  }
  goto LAB_00567fb9;
code_r0x00567fd3:
  pUVar5 = pUVar5 + 0xc;
  iVar13 = iVar13 + 1;
  if (0x656017 < (int)pUVar5) goto code_r0x00567fde;
  goto LAB_00567fcf;
code_r0x00567fde:
  BVar6 = GetCPInfo(CodePage,&local_1c);
  uVar8 = 1;
  if (BVar6 == 1) {
    DAT_009d35c4 = 0;
    puVar14 = &DAT_009d34c0;
    for (iVar13 = 0x40; iVar13 != 0; iVar13 = iVar13 + -1) {
      *puVar14 = 0;
      puVar14 = puVar14 + 1;
    }
    *(undefined1 *)puVar14 = 0;
    if (local_1c.MaxCharSize < 2) {
      DAT_009d33bc = 0;
      DAT_009d33a4 = CodePage;
    }
    else {
      DAT_009d33a4 = CodePage;
      if (local_1c.LeadByte[0] != '\0') {
        pBVar9 = local_1c.LeadByte + 1;
        do {
          bVar3 = *pBVar9;
          if (bVar3 == 0) break;
          for (uVar7 = (uint)pBVar9[-1]; uVar7 <= bVar3; uVar7 = uVar7 + 1) {
            pbVar12 = (byte *)((int)&DAT_009d34c0 + uVar7 + 1);
            *pbVar12 = *pbVar12 | 4;
          }
          pBVar1 = pBVar9 + 1;
          pBVar9 = pBVar9 + 2;
        } while (*pBVar1 != 0);
      }
      do {
        pbVar12 = (byte *)((int)&DAT_009d34c0 + uVar8 + 1);
        *pbVar12 = *pbVar12 | 8;
        uVar8 = uVar8 + 1;
      } while (uVar8 < 0xff);
      DAT_009d35c4 = CTexture__Helper_00568189(CodePage);
      DAT_009d33bc = 1;
    }
    DAT_009d33b0 = 0;
    DAT_009d33b4 = 0;
    DAT_009d33b8 = 0;
  }
  else {
    if (DAT_009d09c0 == 0) {
      iVar13 = -1;
      goto LAB_00568130;
    }
LAB_0056811e:
    CTexture__Helper_005681bc();
  }
LAB_00568123:
  CTexture__Helper_005681e5();
LAB_00567fb9:
  iVar13 = 0;
LAB_00568130:
  CRT__UnlockByIndex(0x19);
  return iVar13;
}
