/* address: 0x004905f0 */
/* name: CUnitAI__Unk_004905f0 */
/* signature: void __fastcall CUnitAI__Unk_004905f0(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnitAI__Unk_004905f0(int param_1)

{
  void *pvVar1;
  int iVar2;
  float fVar3;
  int iVar4;
  int *piVar5;
  float *pfVar6;
  int *piVar7;
  float *pfVar8;
  float *pfVar9;
  int unaff_EDI;
  float *pfVar10;
  int local_b8;
  int local_b0 [12];
  int local_80 [32];

  pfVar9 = (float *)(param_1 + 0x1c4);
  pfVar6 = (float *)&DAT_009c6678;
  iVar2 = 2;
  piVar5 = local_b0;
  do {
    if (pfVar9[2] != 0.0) {
      fVar3 = (float)((int)pfVar9[2] + -1);
      pfVar9[2] = fVar3;
      if (fVar3 == 0.0) {
        *pfVar9 = 0.0;
        (&DAT_009c68a0)[iVar2] = 0;
        (&DAT_009c6904)[iVar2] = 1;
      }
      else {
        *pfVar9 = pfVar9[1] + *pfVar9;
        pfVar9[0xf] = pfVar9[3] + pfVar9[0xf];
        pfVar9[0x10] = pfVar9[4] + pfVar9[0x10];
        pfVar9[0x11] = pfVar9[5] + pfVar9[0x11];
        (&DAT_009c68a0)[iVar2] = 0;
        (&DAT_009c6904)[iVar2] = 1;
        pfVar8 = pfVar9 + 6;
        pfVar10 = pfVar6;
        for (iVar4 = 0x17; iVar4 != 0; iVar4 = iVar4 + -1) {
          *pfVar10 = *pfVar8;
          pfVar8 = pfVar8 + 1;
          pfVar10 = pfVar10 + 1;
        }
        (&DAT_009c68fc)[iVar2] = 1;
        (&DAT_009c68a0)[iVar2] = 1;
        (&DAT_009c6904)[iVar2] = 1;
      }
    }
    fVar3 = *pfVar9;
    pfVar9 = pfVar9 + 0x1d;
    pfVar6 = pfVar6 + 0x17;
    local_b8 = (int)(longlong)ROUND(fVar3 * _DAT_005dc23c);
    piVar5[1] = local_b8;
    *piVar5 = iVar2 + -2;
    iVar4 = iVar2 + -1;
    iVar2 = iVar2 + 1;
    piVar5 = piVar5 + 2;
  } while (iVar4 < 6);
  if (*(int *)(param_1 + 0x1c0) != 0) {
    CDXTexture__Unk_0055e7ae(local_b0,(void *)0x6,8,&LAB_004905d0);
    pvVar1 = *(void **)(param_1 + 0x1c0);
    iVar2 = 0;
    if (0 < (int)pvVar1) {
      pfVar9 = (float *)(param_1 + 8);
      piVar5 = local_80;
      do {
        fVar3 = *pfVar9;
        pfVar9 = pfVar9 + 7;
        local_b8 = (int)(longlong)ROUND(fVar3 * _DAT_005dc23c);
        piVar5[1] = local_b8;
        *piVar5 = iVar2;
        iVar2 = iVar2 + 1;
        piVar5 = piVar5 + 2;
      } while (iVar2 < (int)pvVar1);
    }
    CDXTexture__Unk_0055e7ae(local_80,pvVar1,8,&LAB_004905d0);
    iVar4 = 0;
    iVar2 = *(int *)(param_1 + 0x1c0) + -1;
    if (-1 < iVar2) {
      piVar7 = local_b0 + 1;
      piVar5 = local_80 + iVar2 * 2 + 1;
      do {
        if ((5 < iVar4) || (*piVar5 <= *piVar7)) break;
        CUnitAI__Unk_004903a0((void *)param_1,iVar4,iVar2,unaff_EDI);
        iVar4 = iVar4 + 1;
        piVar7 = piVar7 + 2;
        iVar2 = iVar2 + -1;
        piVar5 = piVar5 + -2;
      } while (-1 < iVar2);
    }
    *(undefined4 *)(param_1 + 0x1c0) = 0;
  }
  return;
}
