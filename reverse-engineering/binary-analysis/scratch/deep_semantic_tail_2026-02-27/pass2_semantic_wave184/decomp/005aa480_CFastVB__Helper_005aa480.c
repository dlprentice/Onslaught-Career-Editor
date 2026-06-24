/* address: 0x005aa480 */
/* name: CFastVB__Helper_005aa480 */
/* signature: int __stdcall CFastVB__Helper_005aa480(void * param_1, void * param_2, uint param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int CFastVB__Helper_005aa480(void *param_1,void *param_2,uint param_3)

{
  ulonglong *puVar1;
  ulonglong uVar2;
  ulonglong uVar3;
  ulonglong uVar4;
  ulonglong uVar5;
  ulonglong uVar6;
  ulonglong uVar7;
  ulonglong uVar8;
  ulonglong uVar9;
  int iVar10;

  puVar1 = param_1;
  if ((int)param_3 < 4) {
    if (param_3 != 0) {
      CTexture__Helper_00575a6b((int)param_1,(int)param_2,param_3);
    }
  }
  else {
    while( true ) {
      for (; 3 < (int)param_3; param_3 = param_3 - 4) {
        uVar7 = (ulonglong)
                CONCAT24((short)((uint)*(undefined4 *)param_2 >> 0x10),*(undefined4 *)param_2) &
                0xffffffff0000ffff;
        uVar3 = (ulonglong)
                CONCAT24((short)((uint)*(undefined4 *)((int)param_2 + 4) >> 0x10),
                         *(undefined4 *)((int)param_2 + 4)) & 0xffffffff0000ffff;
        uVar9 = CONCAT44(-(uint)((int)((uVar7 & DAT_0065e940) >> 0x20) == 0),
                         -(uint)((int)(uVar7 & DAT_0065e940) == 0));
        uVar4 = CONCAT44(-(uint)((int)((uVar3 & DAT_0065e940) >> 0x20) == 0),
                         -(uint)((int)(uVar3 & DAT_0065e940) == 0));
        uVar6 = uVar7 & DAT_0065e960;
        uVar8 = uVar3 & DAT_0065e960;
        iVar10 = (int)((ulonglong)DAT_0065e950 >> 0x20);
        uVar2 = uVar9 & _DAT_0065e970;
        uVar5 = uVar4 & _DAT_0065e970;
        uVar7 = PackedFloatingSUB(CONCAT44(((int)((uVar7 ^ uVar6) >> 0x20) + iVar10 +
                                           (int)(uVar2 >> 0x20)) * 0x2000,
                                           ((int)(uVar7 ^ uVar6) + (int)DAT_0065e950 + (int)uVar2) *
                                           0x2000),uVar9 & _DAT_0065e980);
        uVar9 = PackedFloatingSUB(CONCAT44(((int)((uVar3 ^ uVar8) >> 0x20) + iVar10 +
                                           (int)(uVar5 >> 0x20)) * 0x2000,
                                           ((int)(uVar3 ^ uVar8) + (int)DAT_0065e950 + (int)uVar5) *
                                           0x2000),uVar4 & _DAT_0065e980);
        *puVar1 = uVar7 | CONCAT44((int)(uVar6 >> 0x20) << 0x10,(int)uVar6 << 0x10);
        puVar1[1] = uVar9 | CONCAT44((int)(uVar8 >> 0x20) << 0x10,(int)uVar8 << 0x10);
        puVar1 = puVar1 + 2;
        param_2 = (void *)((int)param_2 + 8);
      }
      if (param_3 == 0) break;
      param_2 = (void *)((int)param_2 + (param_3 - 4) * 2);
      puVar1 = (ulonglong *)((int)puVar1 + (param_3 - 4) * 4);
      param_3 = 4;
    }
  }
  FastExitMediaState();
  return (int)param_1;
}
