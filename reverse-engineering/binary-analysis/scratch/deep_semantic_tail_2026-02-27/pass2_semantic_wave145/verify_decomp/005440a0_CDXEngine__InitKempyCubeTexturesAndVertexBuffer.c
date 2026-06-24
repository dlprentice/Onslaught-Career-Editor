/* address: 0x005440a0 */
/* name: CDXEngine__InitKempyCubeTexturesAndVertexBuffer */
/* signature: void __thiscall CDXEngine__InitKempyCubeTexturesAndVertexBuffer(void * this, void * param_1, void * param_2) */


void __thiscall
CDXEngine__InitKempyCubeTexturesAndVertexBuffer(void *this,void *param_1,void *param_2)

{
  int *piVar1;
  void *pvVar2;
  int iVar3;
  undefined4 *puVar4;
  char *name;
  undefined4 *puVar5;
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 uStack_4;

  uStack_4 = 0xffffffff;
  puStack_8 = &LAB_005d7936;
  pvStack_c = ExceptionList;
  iVar3 = 0;
  name = (char *)((int)this + 0x14);
  ExceptionList = &pvStack_c;
  do {
    CDXEngine__Helper_0048de30(name);
    piVar1 = CTexture__FindTexture(name,0,0,1,1,1);
    *(int **)this = piVar1;
    iVar3 = iVar3 + 1;
    name = name + 0x100;
    this = (void *)((int)this + 4);
  } while (iVar3 < 5);
  if (DAT_008aa908 != (undefined4 *)0x0) {
    (**(code **)*DAT_008aa908)(1);
    DAT_008aa908 = (undefined4 *)0x0;
  }
  pvVar2 = (void *)OID__AllocObject(0x2c,0x2c,s_C__dev_ONSLAUGHT2_DXKempyCube_cp_00650a88,0x52);
  uStack_4 = 0;
  if (pvVar2 == (void *)0x0) {
    DAT_008aa908 = (undefined4 *)0x0;
  }
  else {
    DAT_008aa908 = (undefined4 *)CVBuffer__ctor_like_004fff00(pvVar2);
  }
  uStack_4 = 0xffffffff;
  CVBuffer__Create(0x14,0x14,0x102);
  iVar3 = CVBuffer__Lock(&param_1);
  if (-1 < iVar3) {
    puVar4 = &DAT_006508f0;
    puVar5 = param_1;
    for (iVar3 = 100; iVar3 != 0; iVar3 = iVar3 + -1) {
      *puVar5 = *puVar4;
      puVar4 = puVar4 + 1;
      puVar5 = puVar5 + 1;
    }
    CVBuffer__Unlock();
  }
  ExceptionList = pvStack_c;
  return;
}
