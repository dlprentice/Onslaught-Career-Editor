/* address: 0x00579d33 */
/* name: CDXTexture__InitSurfaceFormatInfoFromDescriptor */
/* signature: int __thiscall CDXTexture__InitSurfaceFormatInfoFromDescriptor(void * this, void * param_1, void * param_2) */


int __thiscall
CDXTexture__InitSurfaceFormatInfoFromDescriptor(void *this,void *param_1,void *param_2)

{
  uint *puVar1;
  int iVar2;
  uint *puVar3;
  uint *puVar4;

  if ((*(void **)((int)this + 4) != (void *)0x0) && (*(int *)((int)this + 0x38) != 0)) {
    OID__FreeObject_Callback(*(void **)((int)this + 4));
  }
  if ((*(void **)((int)this + 8) != (void *)0x0) && (*(int *)((int)this + 0x3c) != 0)) {
    OID__FreeObject_Callback(*(void **)((int)this + 8));
  }
  *(undefined4 *)this = *(undefined4 *)((int)param_1 + 4);
  *(undefined4 *)((int)this + 4) = *(undefined4 *)param_1;
  *(undefined4 *)((int)this + 8) = *(undefined4 *)((int)param_1 + 0x4c);
  puVar1 = (uint *)((int)this + 0x18);
  puVar3 = (uint *)((int)param_1 + 0x28);
  puVar4 = puVar1;
  for (iVar2 = 6; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar4 = *puVar3;
    puVar3 = puVar3 + 1;
    puVar4 = puVar4 + 1;
  }
  *(undefined4 *)((int)this + 0x30) = *(undefined4 *)((int)param_1 + 8);
  *(undefined4 *)((int)this + 0x34) = *(undefined4 *)((int)param_1 + 0xc);
  iVar2 = *(int *)this;
  if (iVar2 < 0x34545845) {
    if (((iVar2 != 0x34545844) && (iVar2 != 0x31545844)) && (iVar2 != 0x32545844)) {
      if (iVar2 == 0x32595559) goto LAB_00579e03;
      if (iVar2 != 0x33545844) goto LAB_00579dbf;
    }
  }
  else if (iVar2 != 0x35545844) {
    if (((iVar2 != 0x42475247) && (iVar2 != 0x47424752)) && (iVar2 != 0x59565955))
    goto LAB_00579dbf;
LAB_00579e03:
    *puVar1 = *puVar1 & 0xfffffffe;
    goto LAB_00579dbf;
  }
  *puVar1 = *puVar1 & 0xfffffffc;
  *(uint *)((int)this + 0x1c) = *(uint *)((int)this + 0x1c) & 0xfffffffc;
LAB_00579dbf:
  *(undefined4 *)((int)this + 0x38) = 0;
  *(undefined4 *)((int)this + 0x3c) = 0;
  *(uint *)((int)this + 0xc) = *(int *)((int)this + 0x20) - *puVar1;
  *(int *)((int)this + 0x10) = *(int *)((int)this + 0x24) - *(int *)((int)this + 0x1c);
  *(int *)((int)this + 0x14) = *(int *)((int)this + 0x2c) - *(int *)((int)this + 0x28);
  return 0;
}
