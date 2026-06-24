/* address: 0x005492b0 */
/* name: CDXEngine__DumpMemoryStats */
/* signature: void __stdcall CDXEngine__DumpMemoryStats(int param_1) */


void CDXEngine__DumpMemoryStats(int param_1)

{
  CMemoryManager__DumpStatsToFile(param_1);
  return;
}
