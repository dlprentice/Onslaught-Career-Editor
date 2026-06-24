/* address: 0x0059d47a */
/* name: CDXTexture__Helper_0059d47a */
/* signature: void __stdcall CDXTexture__Helper_0059d47a(void * param_1) */


void CDXTexture__Helper_0059d47a(void *param_1)

{
  char cVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  void *pvVar5;
  int iVar6;

  *(undefined4 *)((int)param_1 + 0x68) = 0;
  CMeshCollisionVolume__Helper_00594c48((int)param_1);
  uVar3 = *(uint *)((int)param_1 + 0xbc);
  if (*(char *)((int)param_1 + 0x113) == '\0') {
    iVar6 = *(int *)((int)param_1 + 0xb8);
    *(uint *)((int)param_1 + 0xc0) = uVar3;
    *(int *)((int)param_1 + 0xd0) = iVar6;
    *(int *)((int)param_1 + 0xcc) = *(int *)((int)param_1 + 200) + 1;
  }
  else {
    if ((*(byte *)((int)param_1 + 0x60) & 2) == 0) {
      uVar3 = uVar3 + 7 >> 3;
    }
    iVar6 = *(int *)((int)param_1 + 0xb8);
    *(uint *)((int)param_1 + 0xc0) = uVar3;
    iVar4 = (uint)*(byte *)((int)param_1 + 0x114) * 4;
    uVar3 = ((iVar6 - *(int *)(&DAT_005f39bc + iVar4)) + -1 + *(uint *)(&DAT_005f39d8 + iVar4)) /
            *(uint *)(&DAT_005f39d8 + iVar4);
    *(uint *)((int)param_1 + 0xd0) = uVar3;
    *(uint *)((int)param_1 + 0xcc) = (*(byte *)((int)param_1 + 0x119) * uVar3 + 7 >> 3) + 1;
  }
  uVar3 = (uint)*(byte *)((int)param_1 + 0x119);
  uVar2 = *(uint *)((int)param_1 + 0x60);
  if (((uVar2 & 4) != 0) && (*(byte *)((int)param_1 + 0x117) < 8)) {
    uVar3 = 8;
  }
  if ((uVar2 & 0x1000) != 0) {
    cVar1 = *(char *)((int)param_1 + 0x116);
    if (cVar1 == '\x03') {
      uVar3 = (uint)(*(short *)((int)param_1 + 0x10a) != 0) * 8 + 0x18;
    }
    else if (cVar1 == '\0') {
      if (uVar3 < 8) {
        uVar3 = 8;
      }
      if (*(short *)((int)param_1 + 0x10a) != 0) {
        uVar3 = uVar3 * 2;
      }
    }
    else if ((cVar1 == '\x02') && (*(short *)((int)param_1 + 0x10a) != 0)) {
      uVar3 = (uVar3 << 2) / 3;
    }
  }
  if ((char)(uVar2 >> 8) < '\0') {
    cVar1 = *(char *)((int)param_1 + 0x116);
    if (cVar1 == '\x03') {
      uVar3 = 0x20;
    }
    else if (cVar1 == '\0') {
      uVar3 = ((8 < uVar3) - 1 & 0xfffffff0) + 0x20;
    }
    else if (cVar1 == '\x02') {
      uVar3 = ((0x20 < uVar3) - 1 & 0xffffffe0) + 0x40;
    }
  }
  pvVar5 = CMeshCollisionVolume__Helper_0059cc7c
                     (param_1,((iVar6 + 7U & 0xfffffff8) * uVar3 + 7 >> 3) + 1 +
                              ((int)(uVar3 + 7) >> 3));
  *(void **)((int)param_1 + 0xdc) = pvVar5;
  pvVar5 = CMeshCollisionVolume__Helper_0059cc7c(param_1,*(int *)((int)param_1 + 200) + 1);
  *(void **)((int)param_1 + 0xd8) = pvVar5;
  CDXTexture__MemsetByte((int)param_1,pvVar5,0,*(int *)((int)param_1 + 200) + 1);
  *(uint *)((int)param_1 + 0x5c) = *(uint *)((int)param_1 + 0x5c) | 0x40;
  return;
}
