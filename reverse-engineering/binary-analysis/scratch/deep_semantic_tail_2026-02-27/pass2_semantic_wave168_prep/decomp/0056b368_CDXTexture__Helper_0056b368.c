/* address: 0x0056b368 */
/* name: CDXTexture__Helper_0056b368 */
/* signature: uint __cdecl CDXTexture__Helper_0056b368(uint param_1, void * param_2) */


uint __cdecl CDXTexture__Helper_0056b368(uint param_1,void *param_2)

{
  int *piVar1;
  byte bVar2;
  uint uVar3;
  void *pvVar4;
  undefined *puVar5;
  int iVar6;
  undefined4 *puVar7;

  pvVar4 = param_2;
  if ((*(byte *)((int)param_2 + 0xc) & 0x40) != 0) {
LAB_0056b43e:
    piVar1 = (int *)((int)param_2 + 4);
    *piVar1 = *piVar1 + -2;
    if (*piVar1 < 0) {
      param_1 = CRT__WriteWideCharToStream(param_1 & 0xffff,param_2);
    }
    else {
      **(undefined2 **)param_2 = (undefined2)param_1;
      *(int *)param_2 = *(int *)param_2 + 2;
    }
    return param_1;
  }
  uVar3 = *(uint *)((int)param_2 + 0x10);
  if (uVar3 == 0xffffffff) {
    puVar5 = &DAT_00656080;
  }
  else {
    puVar5 = (undefined *)((&DAT_009d32a0)[(int)uVar3 >> 5] + (uVar3 & 0x1f) * 0x24);
  }
  if ((puVar5[4] & 0x80) == 0) goto LAB_0056b43e;
  iVar6 = CFastVB__Helper_00569dfe((int)&param_2,param_1);
  if (iVar6 == -1) {
    puVar7 = (undefined4 *)CTexture__Helper_00567aa8();
    *puVar7 = 0x2a;
    goto LAB_0056b3c5;
  }
  if (iVar6 == 1) {
    piVar1 = (int *)((int)pvVar4 + 4);
    *piVar1 = *piVar1 + -1;
    bVar2 = (byte)param_2;
    if (-1 < *piVar1) {
      **(byte **)pvVar4 = (byte)param_2;
      goto LAB_0056b3e3;
    }
LAB_0056b3ec:
    puVar7 = (undefined4 *)CRT__FlsBuf((int)(char)bVar2,pvVar4);
  }
  else {
    piVar1 = (int *)((int)pvVar4 + 4);
    *piVar1 = *piVar1 + -1;
    if (*piVar1 < 0) {
      puVar7 = (undefined4 *)CRT__FlsBuf((int)(char)(byte)param_2,pvVar4);
    }
    else {
      **(byte **)pvVar4 = (byte)param_2;
      *(int *)pvVar4 = *(int *)pvVar4 + 1;
      puVar7 = (undefined4 *)((uint)param_2 & 0xff);
    }
    if (puVar7 == (undefined4 *)0xffffffff) goto LAB_0056b3c5;
    piVar1 = (int *)((int)pvVar4 + 4);
    *piVar1 = *piVar1 + -1;
    bVar2 = param_2._1_1_;
    if (*piVar1 < 0) goto LAB_0056b3ec;
    **(byte **)pvVar4 = param_2._1_1_;
    param_2._0_1_ = param_2._1_1_;
LAB_0056b3e3:
    puVar7 = (undefined4 *)(uint)(byte)param_2;
    *(int *)pvVar4 = *(int *)pvVar4 + 1;
  }
  if (puVar7 != (undefined4 *)0xffffffff) {
    return CONCAT22((short)((uint)puVar7 >> 0x10),(undefined2)param_1);
  }
LAB_0056b3c5:
  return CONCAT22((short)((uint)puVar7 >> 0x10),0xffff);
}
