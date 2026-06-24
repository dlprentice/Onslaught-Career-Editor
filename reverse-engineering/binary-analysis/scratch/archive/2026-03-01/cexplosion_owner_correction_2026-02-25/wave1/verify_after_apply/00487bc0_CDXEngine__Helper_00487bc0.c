/* address: 0x00487bc0 */
/* name: CDXEngine__Helper_00487bc0 */
/* signature: void __fastcall CDXEngine__Helper_00487bc0(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CDXEngine__Helper_00487bc0(int param_1)

{
  void *pvVar1;
  float fVar2;
  int iVar3;
  char cVar4;
  int *piVar5;
  uint unaff_EBP;
  undefined4 *puVar6;
  int number;
  double dVar7;
  ulonglong uVar8;
  uint local_c;

  iVar3 = DAT_0089c9ac;
  fVar2 = DAT_00672fd0;
  dVar7 = CTexture__Unk_0055dfe7((double)DAT_00672fd0);
  local_c = (uint)(longlong)ROUND(((double)fVar2 - dVar7) * (double)_DAT_005d85bc);
  *(uint *)(param_1 + 0x4c) = local_c & 1;
  if ((DAT_0089ce54 & 8) != 0) {
    if (*(int *)(param_1 + 0x40) != 2) {
      *(uint *)(param_1 + 0x40) = (uint)(*(int *)(DAT_008a9d84 + 8) == 0);
    }
    number = 0;
    if (0 < iVar3) {
      uVar8 = (ulonglong)unaff_EBP;
      puVar6 = &DAT_0089ce08;
      do {
        pvVar1 = (void *)*puVar6;
        if (pvVar1 != (void *)0x0) {
          piVar5 = CGame__GetCamera(&DAT_008a9a98,number);
          cVar4 = (**(code **)(*piVar5 + 0x1c))();
          if (cVar4 != '\0') {
            CExplosionInitThing__Unk_004879e0((void *)param_1,pvVar1,number,(float)uVar8);
          }
        }
        number = number + 1;
        puVar6 = puVar6 + 1;
      } while (number < iVar3);
    }
    DAT_009c68ad = 1;
    DAT_009c6910 = 1;
    RenderState_Set(0xe,1);
    RenderState_Set(0x17,4);
    RenderState_Set(7,1);
    DAT_009c68ac = 1;
    DAT_009c690d = 1;
    D3DStateCache__SetSlotMode4or5(0);
    D3DStateCache__SetState114Raw(0,1,1);
    D3DStateCache__SetState114Raw(0,2,1);
    D3DStateCache__SetState114Raw(0,6,2);
    D3DStateCache__SetState114Raw(0,5,2);
    D3DStateCache__SetMipFilterLinear(0);
  }
  return;
}
