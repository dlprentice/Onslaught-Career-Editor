/* address: 0x004f2a30 */
/* name: CTexture__ClearOut */
/* signature: void CTexture__ClearOut(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CTexture__ClearOut(void)

{
  void *pvVar1;
  void *this;
  void *pvVar2;
  char *format;
  char local_100 [256];

  pvVar1 = DAT_0083d9b0;
  pvVar2 = DAT_0083d9b0;
  if (DAT_0083d9b4 != 0) {
    *(int *)(DAT_0083d9b4 + 0xa4) = *(int *)(DAT_0083d9b4 + 0xa4) + -1;
    DAT_0083d9b4 = 0;
    pvVar1 = DAT_0083d9b0;
    pvVar2 = DAT_0083d9b0;
  }
  while (this = pvVar1, DAT_0083d9b0 = pvVar2, this != (void *)0x0) {
    pvVar1 = *(void **)((int)this + 0xa0);
    if (*(int *)((int)this + 0xa4) == 0) {
      CTexture__Release(this);
      pvVar2 = DAT_0083d9b0;
    }
  }
  if (pvVar2 == (void *)0x0) {
    format = s_No_texture_resource_leaks_00632f94;
  }
  else {
    DebugTrace(s________________________00633024);
    DebugTrace(s_Texture_resource_leaks_0063300c);
    DebugTrace(s________________________00632ff0);
    do {
      sprintf(local_100,s_Texture___s__leaked___refcount___00632fcc);
      DebugTrace(local_100);
      pvVar2 = *(void **)((int)pvVar2 + 0xa0);
    } while (pvVar2 != (void *)0x0);
    format = s________________________00632fb0;
  }
  DebugTrace(format);
  for (pvVar1 = DAT_0083d9b0; pvVar2 = DAT_0083d9b0, pvVar1 != (void *)0x0;
      pvVar1 = *(void **)((int)pvVar1 + 0xa0)) {
    *(undefined4 *)((int)pvVar1 + 0xa4) = 0;
  }
  while (pvVar1 = pvVar2, pvVar1 != (void *)0x0) {
    pvVar2 = *(void **)((int)pvVar1 + 0xa0);
    if (*(int *)((int)pvVar1 + 0xa4) == 0) {
      CTexture__Release(pvVar1);
    }
  }
  return;
}
