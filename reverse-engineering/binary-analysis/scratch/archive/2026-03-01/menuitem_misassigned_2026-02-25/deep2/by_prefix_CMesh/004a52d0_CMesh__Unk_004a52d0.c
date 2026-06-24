/* address: 0x004a52d0 */
/* name: CMesh__Unk_004a52d0 */
/* signature: void CMesh__Unk_004a52d0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CMesh__Unk_004a52d0(void)

{
  void *pvVar1;
  bool bVar2;
  void *pvVar3;
  char local_100 [256];

  pvVar3 = DAT_00704adc;
  if (DAT_00704adc != (void *)0x0) {
    CExplosionInitThing__Unk_004adf90(DAT_00704adc);
    OID__FreeObject(pvVar3);
    DAT_00704adc = (void *)0x0;
  }
  do {
    bVar2 = true;
    pvVar3 = DAT_00704ad8;
    if (DAT_00704ad8 == (void *)0x0) break;
    do {
      pvVar1 = *(void **)((int)pvVar3 + 0x158);
      if ((*(int *)((int)pvVar3 + 0x170) == 0) && (bVar2 = false, pvVar3 != (void *)0x0)) {
        CMesh__Unk_004a50b0(pvVar3);
        OID__FreeObject(pvVar3);
      }
      pvVar3 = pvVar1;
    } while (pvVar1 != (void *)0x0);
  } while (!bVar2);
  pvVar3 = DAT_00704ad8;
  if (DAT_00704ad8 == (void *)0x0) {
    DebugTrace(s_____________________0062f988);
    DebugTrace(s_No_mesh_resource_leaks__0062f904);
    DebugTrace(s_____________________0062f958);
    return;
  }
  DebugTrace(s_____________________0062f988);
  DebugTrace(s_Mesh_resource_leaks_0062f970);
  DebugTrace(s_____________________0062f958);
  do {
    sprintf(local_100,s_Mesh___s__leaked___refcount__d_0062f938);
    DebugTrace(local_100);
    pvVar3 = *(void **)((int)pvVar3 + 0x158);
  } while (pvVar3 != (void *)0x0);
  DebugTrace(s_____________________0062f920);
  return;
}
