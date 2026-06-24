/* address: 0x00594d5c */
/* name: CDXTexture__ApplyPngRowTransforms */
/* signature: void __stdcall CDXTexture__ApplyPngRowTransforms(void * param_1) */


void CDXTexture__ApplyPngRowTransforms(void *param_1)

{
  int iVar1;

  if (*(int *)((int)param_1 + 0xdc) == 0) {
    CDXTexture__ThrowDecodeError(param_1,0x5eeadc);
  }
  if ((*(byte *)((int)param_1 + 0x61) & 0x10) != 0) {
    if (*(char *)((int)param_1 + 0xf8) == '\x03') {
      CDXTexture__ExpandIndexedRowToRgbOrRgba
                ((void *)((int)param_1 + 0xf0),*(int *)((int)param_1 + 0xdc) + 1,
                 *(int *)((int)param_1 + 0x104),*(int *)((int)param_1 + 0x15c),
                 (uint)*(ushort *)((int)param_1 + 0x10a));
    }
    else {
      if (*(short *)((int)param_1 + 0x10a) == 0) {
        iVar1 = 0;
      }
      else {
        iVar1 = (int)param_1 + 0x160;
      }
      CFastVB__Helper_005944e3
                ((void *)((int)param_1 + 0xf0),*(int *)((int)param_1 + 0xdc) + 1,iVar1);
    }
  }
  if (((*(byte *)((int)param_1 + 0x61) & 0x20) != 0) && (*(char *)((int)param_1 + 0x116) != '\x03'))
  {
    CFastVB__Helper_00593f8a
              ((void *)((int)param_1 + 0xf0),(void *)(*(int *)((int)param_1 + 0xdc) + 1),
               *(int *)((int)param_1 + 0x138),*(void **)((int)param_1 + 0x144),
               *(int *)((int)param_1 + 300));
  }
  if ((*(byte *)((int)param_1 + 0x61) & 4) != 0) {
    CFastVB__Helper_00593d0b
              ((void *)((int)param_1 + 0xf0),(void *)(*(int *)((int)param_1 + 0xdc) + 1));
  }
  if ((*(byte *)((int)param_1 + 0x60) & 0x40) != 0) {
    CFastVB__Helper_00594836
              ((void *)((int)param_1 + 0xf0),(void *)(*(int *)((int)param_1 + 0xdc) + 1),
               *(int *)((int)param_1 + 0x174),*(int *)((int)param_1 + 0x178));
    if (*(int *)((int)param_1 + 0xf4) == 0) {
      CDXTexture__ThrowDecodeError(param_1,0x5eeab8);
    }
  }
  if ((*(byte *)((int)param_1 + 0x60) & 8) != 0) {
    CFastVB__Helper_00593b92
              ((void *)((int)param_1 + 0xf0),(void *)(*(int *)((int)param_1 + 0xdc) + 1),
               (void *)((int)param_1 + 0x155));
  }
  if ((*(byte *)((int)param_1 + 0x60) & 4) != 0) {
    CFastVB__Helper_00593a81((void *)((int)param_1 + 0xf0),*(int *)((int)param_1 + 0xdc) + 1);
  }
  if ((*(byte *)((int)param_1 + 0x60) & 1) != 0) {
    CDXTexture__SwapRgbBgrChannelOrder
              ((void *)((int)param_1 + 0xf0),(void *)(*(int *)((int)param_1 + 0xdc) + 1));
  }
  if ((*(byte *)((int)param_1 + 0x61) & 0x80) != 0) {
    CFastVB__Helper_00593d51
              ((void *)((int)param_1 + 0xf0),*(int *)((int)param_1 + 0xdc) + 1,
               (uint)*(ushort *)((int)param_1 + 0x11e),*(uint *)((int)param_1 + 0x5c));
  }
  if ((*(byte *)((int)param_1 + 0x60) & 0x10) != 0) {
    CDXTexture__Swap16BitSampleByteOrder
              ((void *)((int)param_1 + 0xf0),(void *)(*(int *)((int)param_1 + 0xdc) + 1));
  }
  return;
}
