#' @description Combine histogram and pie plot
#'
#' @param x a list
#' @param scale a value between 0 and 1 
#' @return A plot combined with hist and pie
#' @examples
#' hist_pie(x)
#' @export
hist_pie <- function(x, scale){
  # set temp path to store pie plot
  temp_path <- tempdir()
  #png(paste0(temp_path,"/pie.png"), width = 480, height = 480)
  p1 = plot_pie(x)
  #print(p1)
  #dev.off()
  ggsave(paste0(temp_path,"/pie.png"), p1, width = 10, height = 10, units = "cm")
  levels = x %>% table(dnn = "type") %>% as.data.frame() %>% arrange(desc(Freq)) %>% pull(type)
  max_y = x %>% table(dnn = "type") %>% max()
  img = png::readPNG(paste0(temp_path, "/pie.png"))
  g <- grid::rasterGrob(img, interpolate=TRUE)
  x %>% table(dnn = "type") %>% as.data.frame() %>% arrange(desc(Freq)) %>% 
    ggplot(aes(x = factor(type, levels = levels), y = Freq)) + 
    geom_bar(stat = "identity") + theme_bw() + theme(axis.title = element_blank(), 
                                                     axis.text.x = element_text(size = 12)) + 
    annotation_custom(g, xmin=(1 + length(unique(x)))*(1-scale), 
                      xmax= 1 +length(unique(x)), 
                      ymin = max(max_y)*(1-scale), 
                      ymax = max(max_y)
                      )
}

#' @description Combine histogram and pie plot
#'
#' @param x a list
#' @return A plot combined with hist and pie
#' @examples
#' hist_pie(x)
#' @export
plot_pie <- function(x){
  if(length(unique(x)) > 8){
    message("Number of types is more than 8, please select another way to demonstrate your data.")
  }else{
  df_plot <- x %>% table(dnn = "Category") %>% as.data.frame() %>% 
    arrange(desc(Freq)) %>% group_by(Category) %>% 
    mutate(prop = Freq/length(x))  
  df_plot$y1 = c(0, cumsum(df_plot$prop)[-nrow(df_plot)])
  df_plot$pos = df_plot$prop/2 + df_plot$y1 
  ggplot(df_plot %>% arrange(pos), 
         aes(x =  "", y = prop, 
             fill = factor(Category, levels = df_plot %>% arrange(desc(pos)) %>% pull(Category)))) + 
    geom_bar(stat = "identity") + coord_polar("y", start = 0) + 
    ggrepel::geom_label_repel(aes(y= pos,label = paste(Category,round(100*prop, 2))), size=5, show.legend = F, nudge_x = 1) + theme_bw() + 
    theme(legend.position = "none", axis.title = element_blank(), axis.text = element_blank()) + ggsci::scale_fill_jco() +
    cowplot::panel_border(remove = TRUE)
  
  }
}



#' @description add new point to sfc class
#'
#' @param shp a sf class that will be concatenated.
#' @param point_x a list having the x value of the points that will be added.
#' @param point_y a list having the y value of the points that will be added.
#' @param NAME the name of the points.
#' @param KIND the kind of the points.
#' @param crs the crs that being added.
#' @return A binded sf class
#' @examples
#' add_sfc_to_point_nj(nj_build, point_x = c(118,118.5),point_y = c(31.0,31.2), NAME= c("test1","test2"), KIND = c("a","b"))
#' @export
add_sfc_to_point_nj <- function(shp, point_x, point_y,NAME, KIND,crs = 4326){
  pt1 = st_point(point_x)
  pt2 = st_point(point_y)
  sfc = st_sfc(pt1, pt2)
  d = st_sf(data.frame(NAME=NAME,KIND = KIND,  geom=sfc), crs = crs)
  return(rbind(shp,d))
}

#' @description add new point to sfc class
#'
#' @param point_x a list having the x value of the points that will be added.
#' @param point_y a list having the y value of the points that will be added.
#' @param NAME the name of the points.
#' @param KIND the kind of the points.
#' @param crs the crs that being added.
#' @return A binded sf class
#' @examples
#' add_sfc_to_point_nj(nj_build, point_x = c(118,118.5),point_y = c(31.0,31.2), NAME= c("test1","test2"), KIND = c("a","b"))
#' @export
create_sfc_point <- function(point_x, point_y,NAME, KIND,crs = 4326){
  pt1 = st_point(point_x)
  pt2 = st_point(point_y)
  sfc = st_sfc(pt1, pt2)
  d = st_sf(data.frame(NAME=NAME,KIND = KIND,  geom=sfc), crs = crs)
  return(d)
}


