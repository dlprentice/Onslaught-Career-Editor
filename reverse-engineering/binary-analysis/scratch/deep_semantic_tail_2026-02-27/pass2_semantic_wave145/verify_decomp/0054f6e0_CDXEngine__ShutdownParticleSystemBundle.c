/* address: 0x0054f6e0 */
/* name: CDXEngine__ShutdownParticleSystemBundle */
/* signature: void __fastcall CDXEngine__ShutdownParticleSystemBundle(void * param_1) */


void __fastcall CDXEngine__ShutdownParticleSystemBundle(void *param_1)

{
  int iVar1;
  void *obj;

  iVar1 = *(int *)param_1;
  while (iVar1 != 0) {
    iVar1 = *(int *)(*(int *)param_1 + 0x68);
    CParticle__Destroy();
    *(undefined4 *)(*(int *)param_1 + 0x68) = *(undefined4 *)((int)param_1 + 8);
    *(undefined4 *)((int)param_1 + 8) = *(undefined4 *)param_1;
    *(int *)param_1 = iVar1;
  }
  CParticleManager__ClearParticleOwnerBacklinks();
  CParticleManager__PruneDeadOwnerLinks();
  CParticleManager__CleanupHandles();
  obj = *(void **)((int)param_1 + 0xc);
  if (obj != (void *)0x0) {
    CParticleManager__Shutdown();
    OID__FreeObject(obj);
  }
  return;
}
