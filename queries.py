def query_datos(inicio, fin):
    inicio_str = inicio.strftime("%Y-%m-%d")
    fin_str = fin.strftime("%Y-%m-%d")
    return f"""
        SELECT DATE(iv.transmit_ts) AS fecha,
               lt.label_type_desc,
               SUM(unit_qty) AS cajas
        FROM dc_sys_invoice:invoice AS iv
        INNER JOIN (
            SELECT DISTINCT shipment_id, dest_store_nbr
            FROM dc_sys_order_prcss:container
            WHERE (dest_store_nbr IN (117,118) AND dc_sel_section_id NOT IN (150,110,125)
                   OR dest_store_nbr NOT IN (117,118))
        ) AS a ON a.shipment_id = iv.shipment_id AND a.dest_store_nbr = iv.store_nbr
        INNER JOIN dc_sys_invoice:invoice_line AS il ON il.invoice_id = iv.invoice_id
        LEFT JOIN dc_sys_order_prcss:shipping_unit AS su ON su.shipping_unit_id = il.shipping_unit_id
        LEFT JOIN dc_sys_common:label_type_txt AS lt 
               ON lt.label_type_code = su.label_type_code AND lt.language_code = 101
        WHERE DATE(iv.transmit_ts) BETWEEN '{inicio_str}' AND '{fin_str}'
          AND iv.invoice_status_cd NOT IN ('01')
        GROUP BY 1,2
        ORDER BY 1
    """


def query_dummy(fecha):
    """
    Devuelve la query para contar container_tag_id por fecha
    """
    fecha_str = fecha.strftime("%Y-%m-%d")
    return f"""
    select count(distinct container_tag_id)
    from dc_sys_order_prcss:container as co
    inner join dc_sys_order_prcss:shipment as sh on sh.shipment_id=co.shipment_id
    inner join dc_sys_order_prcss:load as lo on lo.load_id=sh.load_id
    inner join dc_sys_order_prcss:shipping_unit as su on su.container_id=co.container_id and su.shipment_id=sh.shipment_id
    inner join dc_sys_invoice:invoice as iv on iv.load_id=sh.load_id and iv.shipment_id=su.shipment_id
    inner join dc_sys_receiving:receiving_unit as ru on ru.rcv_unit_id=su.rcv_unit_id
    where date(iv.transmit_ts) = '{fecha_str}'
      and (co.dest_store_nbr in (117,118) and co.dc_sel_section_id not in (150,110,125) 
           or co.dest_store_nbr not in (117,118))
      and iv.invoice_status_cd not in ('01')
    """

def query_cdp(fecha):
    fecha_str = fecha.strftime("%Y-%m-%d")
    return f"""
    select distinct a.order_date,
           sum(round(b.order_qty/d.whpk_qty)) as Solicitado,
           sum(round(c.pre_alloc_qty/d.whpk_qty)) as Prealocado
    from dc_sys_order_prcss:informix.warehouse_order a
    inner join dc_sys_order_prcss:informix.whs_order_line b on b.whs_order_nbr = a.whs_order_nbr
    left outer join dc_sys_order_prcss:informix.alloc_order_line c on a.whs_order_nbr = c.whs_order_nbr 
        and c.whs_order_line_nbr = b.whs_order_line_nbr
    left join dc_sys_order_prcss:informix.alloc_order aoh on c.alloc_order_nbr=aoh.alloc_order_nbr
    inner join dc_sys_common:informix.item d on d.item_nbr = b.item_nbr
    where c.order_status_code not in ('VO')
      and a.order_date = '{fecha_str}'
      and a.order_store_nbr not in (117,118)
    group by 1
    order by Solicitado desc
    """