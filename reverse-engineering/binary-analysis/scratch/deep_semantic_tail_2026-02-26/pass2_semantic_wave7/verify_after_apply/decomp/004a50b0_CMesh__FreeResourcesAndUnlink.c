/* address: 0x004a50b0 */
/* name: CMesh__FreeResourcesAndUnlink */
/* signature: void __fastcall CMesh__FreeResourcesAndUnlink(void * param_1) */


void __fastcall CMesh__FreeResourcesAndUnlink(void *param_1)

{
  void *pvVar1;
  void *pvVar2;
  int iVar3;

  pvVar1 = (void *)0x0;
  pvVar2 = DAT_00704ad8;
  do {
    if (pvVar2 == (void *)0x0) {
LAB_004a50f5:
      iVar3 = *(int *)param_1;
      if (iVar3 != 0) {
        CDXLandscape__Helper_0055db0a(iVar3,0x24,*(int *)(iVar3 + -4),CMesh__Helper_004adf90);
        OID__FreeObject((void *)(iVar3 + -4));
        *(undefined4 *)param_1 = 0;
      }
      if (*(int *)((int)param_1 + 0x160) != 0) {
        iVar3 = 0;
        if (0 < *(int *)((int)param_1 + 0x15c)) {
          do {
            pvVar1 = *(void **)(*(int *)((int)param_1 + 0x160) + iVar3 * 4);
            if (pvVar1 != (void *)0x0) {
              CMeshPart__FreeResources((int)pvVar1);
              OID__FreeObject(pvVar1);
              *(undefined4 *)(*(int *)((int)param_1 + 0x160) + iVar3 * 4) = 0;
            }
            iVar3 = iVar3 + 1;
          } while (iVar3 < *(int *)((int)param_1 + 0x15c));
        }
        if (*(void **)((int)param_1 + 0x160) != (void *)0x0) {
          OID__FreeObject(*(void **)((int)param_1 + 0x160));
          *(undefined4 *)((int)param_1 + 0x160) = 0;
        }
      }
      if (*(void **)((int)param_1 + 0x20) != (void *)0x0) {
        OID__FreeObject(*(void **)((int)param_1 + 0x20));
        *(undefined4 *)((int)param_1 + 0x20) = 0;
      }
      if (*(void **)((int)param_1 + 0x18) != (void *)0x0) {
        OID__FreeObject(*(void **)((int)param_1 + 0x18));
        *(undefined4 *)((int)param_1 + 0x18) = 0;
      }
      iVar3 = *(int *)((int)param_1 + 8);
      if (iVar3 != 0) {
        *(int *)(iVar3 + 0x170) = *(int *)(iVar3 + 0x170) + -1;
        *(undefined4 *)((int)param_1 + 8) = 0;
      }
      if (*(void **)((int)param_1 + 0x150) != (void *)0x0) {
        OID__FreeObject(*(void **)((int)param_1 + 0x150));
        *(undefined4 *)((int)param_1 + 0x150) = 0;
      }
      return;
    }
    if (pvVar2 == param_1) {
      if (pvVar2 != (void *)0x0) {
        if (pvVar1 == (void *)0x0) {
          DAT_00704ad8 = *(void **)((int)param_1 + 0x158);
        }
        else {
          *(undefined4 *)((int)pvVar1 + 0x158) = *(undefined4 *)((int)param_1 + 0x158);
        }
      }
      goto LAB_004a50f5;
    }
    pvVar1 = pvVar2;
    pvVar2 = *(void **)((int)pvVar2 + 0x158);
  } while( true );
}
